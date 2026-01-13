#!/bin/bash
set -e

bold=$(tput bold)
normal=$(tput sgr0)

IMAGE_URL="https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-05-28/2021-05-07-raspios-buster-armhf-lite.zip"

ZIP_FILENAME=$( basename "$IMAGE_URL" )
IMAGE_FILENAME="${ZIP_FILENAME%.*}.img"

echo

while [ -z "$sd_device" ]; do
    read -p "SD card device [/dev/mmcblk0]: " sd_device

    if [ -z "$sd_device" ]; then
        sd_device="/dev/mmcblk0"
    fi

    set +e
    sd_model=$( fdisk -l /dev/mmcblk0 | head -1 )
    if [ $? -ne 0 ]; then
        echo "Cannot use ${sd_device}. Try one of the following:"
        lsblk -np -o TYPE,NAME,MODEL,SIZE | grep "^disk" | cut -d' ' -f 2-
        echo

        sd_device=""
    fi
    set -e
done

read -p "Wireless network SSID: " wifi_ssid
read -p "Wireless network password: " wifi_psk
read -p "Scene name: " scene
read -p "Cabinet name: " cabinet
read -p "Client token (from cabinet admin page): " token
read -p "Reader ID (blue or gold): " reader_id
read -p "Configure as router? [Y/n]: " configure_router
read -p "Configure stats client? [Y/n]: " configure_stats

configure_router=${configure_router:-y}
configure_router=${configure_router:0:1}
configure_router=${configure_router,,}

configure_stats=${configure_stats:-y}
configure_stats=${configure_stats:0:1}
configure_stats=${configure_stats,,}

if [ -e "$HOME/.ssh/authorized_keys" ]; then
    authorized_keys_default=$( realpath "$HOME/.ssh/authorized_keys" )
elif [[ ! -z "$SUDO_USER" && -e "$( getent passwd "$SUDO_USER" | cut -d':' -f 6 )/.ssh/authorized_keys" ]]; then
    authorized_keys_default=$( realpath "$( getent passwd "$SUDO_USER" | cut -d':' -f 6 )/.ssh/authorized_keys" )
else
    authorized_keys_default="none"
fi

read -p "SSH authorized keys file [${authorized_keys_default}]: " authorized_keys
if [ -z "$authorized_keys" ]; then
    authorized_keys="$authorized_keys_default"
fi

if [ ! -e "$authorized_keys" ]; then
    echo "WARNING: Could not find authorized keys file. You will not be able to SSH to this system."
    echo
fi

hostname="hivemind-${scene,,}-${cabinet,,}-${reader_id,,}"

echo
echo "THIS WILL OVERWRITE ALL DATA ON THE TARGET DEVICE: ${sd_device} (${sd_model})"
echo "Please make sure this is okay. Press Enter to continue."
read

mount | grep "^${sd_device}" | cut -d ' ' -f 3 | xargs -r umount

# Download OS image
if [ ! -e "$IMAGE_FILENAME" ]; then
    echo
    echo "Downloading OS..."

    wget "$IMAGE_URL"
    unzip "$ZIP_FILENAME"
fi

# Write to SD card
echo
echo "Writing image to SD card..."

dd if="$IMAGE_FILENAME" of="$sd_device" bs=4M conv=fsync status=progress
sync

# Mount SD card
tempdir=$( mktemp -d )
rootfs="${tempdir}/rootfs"
boot="${tempdir}/boot"

mkdir -p "$boot" "$rootfs"

mount -t vfat "${sd_device}p1" "$boot"
mount -t ext4 "${sd_device}p2" "$rootfs"

# Create config files
echo
echo "Creating config files..."

touch "${boot}/ssh"
echo "$hostname" > "${rootfs}/etc/hostname"

hosts_file=$( mktemp )
grep -v "raspberrypi" "${rootfs}/etc/hosts" > "$hosts_file"
echo "127.0.1.1       $hostname" >> "$hosts_file"
mv "$hosts_file" "${rootfs}/etc/hosts"

cat > "${rootfs}/etc/wpa_supplicant/wpa_supplicant.conf" <<EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=us

EOF

wpa_passphrase "${wifi_ssid}" "${wifi_psk}" | sudo tee -a "${rootfs}/etc/wpa_supplicant/wpa_supplicant.conf"

# Networking and router
if [ "$configure_router" != "n" ]; then
    cat >> "${rootfs}/etc/dhcpcd.conf" <<EOF
interface eth0
static ip_address=10.68.182.1
static domain_name_servers=8.8.8.8
EOF

    cat > "${rootfs}/etc/dhcp/dhcpd.conf" <<EOF
ddns-update-style none;
option domain-name "hivemind.local";
option domain-name-servers 8.8.8.8, 8.8.4.4, 10.68.182.1;
default-lease-time 3600;
max-lease-time 86400;
authoritative;
log-facility local7;

subnet 10.68.182.0 netmask 255.255.255.0 {
    range 10.68.182.100 10.68.182.100;
    option routers 10.68.182.1;
}
EOF

    cat > "${rootfs}/etc/default/isc-dhcp-server" <<EOF
INTERFACESv4="eth0"
INTERFACESv6=""
EOF

fi

# Config files
mkdir -p "${rootfs}/home/hivemind"
cat > "${rootfs}/home/hivemind/nfc-config.json" <<EOF
{
  "pin_config": [
    { "player_id": $([ "$reader_id" == "blue" ] && echo "4" || echo "3" ), "button": 22, "light": 21 },
    { "player_id": $([ "$reader_id" == "blue" ] && echo "6" || echo "5" ), "button": 12, "light": 16 },
    { "player_id": $([ "$reader_id" == "blue" ] && echo "2" || echo "1" ), "button": 19, "light": 18 },
    { "player_id": $([ "$reader_id" == "blue" ] && echo "8" || echo "7" ), "button": 13, "light": 15 },
    { "player_id": $([ "$reader_id" == "blue" ] && echo "10" || echo "9" ), "button": 24, "light": 23 }
  ],
  "scene": "${scene,,}",
  "cabinet": "${cabinet,,}",
  "token": "${token}",
  "reader": "${reader_id,,}",
  "usb_device": "usb:072f:2200",
  "log_file": "/home/hivemind/nfc-reader.log",
  "light_mode": "low",
  "button_mode": "low",
  "pins_low": [26]
}
EOF

if [ ]; then
    cat > "${rootfs}/home/hivemind/config.json" <<EOF
{
  "cabinets": [
    {
      "sceneName": "${scene,,}",
      "cabinetName": "${cabinet,,}",
      "token": "${token}",
      "url": "ws://10.68.182.100:12749"
    }
  ],
  "servers": [
    {
      "name": "HiveMind",
      "url": "wss://kqhivemind.com/ws/stats_listener/v3"
    }
  ]
}
EOF

fi

# Authorized keys
if [ -e "$authorized_keys" ]; then
    mkdir -p "${rootfs}/home/hivemind/.ssh"
    cp "$authorized_keys" "${rootfs}/home/hivemind/.ssh/authorized_keys"
fi

# NFC modules
cat >> "${rootfs}/etc/modprobe.d/blacklist.conf" <<EOF
install nfc /bin/false
install pn533 /bin/false
install pn533_usb /bin/false
EOF

# Create first boot script
echo
echo "Creating first boot scripts..."

cat > "${rootfs}/usr/lib/systemd/system/hivemind-first-boot.service" <<EOF
[Unit]
Description=HiveMind initial setup
After=regenerate_ssh_host_keys.service apt-daily.service time-sync.target
Wants=time-sync.target

[Service]
Type=oneshot
ExecStart=/root/firstboot.sh
ExecStartPost=/bin/systemctl disable hivemind-first-boot
ExecStartPost=/usr/sbin/reboot

[Install]
WantedBy=multi-user.target
EOF

ln -s /lib/systemd/system/hivemind-first-boot.service "${rootfs}/etc/systemd/system/multi-user.target.wants/hivemind-first-boot.service"

cat > "${rootfs}/root/firstboot.sh" <<EOF
#!/bin/bash
set -e

usermod -L pi
useradd -m -U -G sudo,gpio,plugdev -p "$( openssl passwd --crypt HiveMind123 )" hivemind
usermod hivemind -p HiveMind123
cat /etc/sudoers | sed 's/^\%sudo.*$/%sudo  ALL=(ALL) NOPASSWD:ALL/' > /tmp/sudoers
chown root:root /tmp/sudoers
chmod 600 /tmp/sudoers
mv /tmp/sudoers /etc/sudoers

chown -R hivemind:hivemind /home/hivemind
chmod 700 "/home/hivemind/.ssh"
chmod 400 "/home/hivemind/.ssh/authorized_keys"
chmod +x /home/hivemind/firstboot.sh

sudo -i -u hivemind /home/hivemind/firstboot.sh >> /var/log/hivemind-firstboot.log 2>&1
EOF

chmod +x "${rootfs}/root/firstboot.sh"

cat > "${rootfs}/home/hivemind/hivemind-nfc-client.sh" <<EOF
#!/bin/bash
if [ -e /boot/nfc-config.json ]; then
   cp /boot/nfc-config.json /home/hivemind/nfc-config.json
fi

pip3 install --upgrade hivemind-nfc-reader
/home/hivemind/.local/bin/hivemind-nfc-reader /home/hivemind/nfc-config.json
EOF

chmod +x "${rootfs}/home/hivemind/hivemind-nfc-client.sh"

cat > "${rootfs}/home/hivemind/firstboot.sh" <<EOF
#!/bin/bash
set -e

cd /home/hivemind

while [[ -z \$( timedatectl status | grep 'System clock synchronized: yes' ) ]]; do sleep 1; done
while sudo fuser /var/{lib/{dpkg,apt/lists},cache/apt/archives}/lock* >/dev/null 2>&1; do sleep 1; done
sudo apt update
while ! sudo apt-get -o Dpkg::Options::='--force-confold' -y install isc-dhcp-server firewalld python3-pip python3-venv libnfc-dev; do sleep 1; done

pip3 install hivemind_nfc_reader

sudo systemctl daemon-reload
sudo systemctl enable hivemind-nfc-reader
EOF

cat > "${rootfs}/etc/udev/rules.d/50-usb-perms.rules" <<EOF
SUBSYSTEM=="usb", ATTRS{idVendor}=="072f", ATTRS{idProduct}=="2200", GROUP="plugdev", MODE="0660"
EOF

cat > "${rootfs}/lib/systemd/system/hivemind-nfc-reader.service" <<EOF
[Unit]
Description=HiveMind NFC Reader Service

[Service]
ExecStart=/home/hivemind/hivemind-nfc-client.sh
User=hivemind

[Install]
WantedBy=multi-user.target
EOF

if [ "$configure_stats" != "n" ]; then
    cat > "${rootfs}/home/hivemind/hivemind-client.sh" <<EOF
#!/bin/bash
export PATH=$PATH:/usr/local/node/bin
cd /home/hivemind

if [ -e /boot/config.json ]; then
   cp /boot/config.json /home/hivemind/config.json
fi

npm upgrade @kqhivemind/hivemind-client
npx hivemind-client config.json | sudo tee -a /dev/tty0
EOF
    chmod +x "${rootfs}/home/hivemind/hivemind-client.sh"

    cat >> "${rootfs}/home/hivemind/firstboot.sh" <<EOF
wget https://nodejs.org/dist/v11.15.0/node-v11.15.0-linux-armv6l.tar.gz
tar xfz node-v11.15.0-linux-armv6l.tar.gz
sudo mv node-v11.15.0-linux-armv6l /usr/local/node
export PATH=$PATH:/usr/local/node/bin

/usr/local/node/bin/npm install @kqhivemind/hivemind-client
sudo env PATH=$PATH:/usr/local/node/bin npm install -g pm2
pm2 start /home/hivemind/hivemind-client.sh --name hivemind-client
sudo env PATH=$PATH:/usr/local/node/bin /usr/local/node/bin/pm2 startup systemd -u hivemind --hp /home/hivemind
pm2 save
EOF
fi

if [ "$configure_router" != "n" ]; then cat >> "${rootfs}/home/hivemind/firstboot.sh" <<EOF
sudo firewall-cmd --zone=home --add-interface=eth0
sudo firewall-cmd --zone=public --add-interface=wlan0
sudo firewall-cmd --zone=public --add-masquerade
sudo firewall-cmd --zone=home --add-service=dns
sudo firewall-cmd --zone=home --add-service=dhcp
sudo firewall-cmd --runtime-to-permanent
EOF
fi

# Cleanup
sync
umount "$boot"
umount "$rootfs"
rm -rf "$tempdir"

echo "All done. After booting, your Raspberry Pi's hostname will be:"
echo "  ${bold}${hostname}${normal}"
echo "Configuration on first boot may take a while. Please leave your Pi turned"
echo "on until the card reader beeps when a card is tapped."
echo
