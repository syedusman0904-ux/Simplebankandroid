# Simple Bank Android

## Project files
- main.py — bank/database logic
- app.py — Kivy Android GUI
- buildozer.spec — APK build configuration

## Exact Termux build commands

Install Termux packages:
pkg update -y
pkg upgrade -y
pkg install -y proot-distro git wget unzip

Install Debian:
proot-distro install debian
proot-distro login debian

Inside Debian:
apt update
apt install -y python3 python3-pip python3-venv git zip unzip openjdk-17-jdk build-essential libffi-dev libssl-dev autoconf automake libtool pkg-config zlib1g-dev

Create environment:
python3 -m venv ~/venv
. ~/venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython

Copy project from Termux home:
cp -r /data/data/com.termux/files/home/SimpleBankAndroid ~/SimpleBankAndroid
cd ~/SimpleBankAndroid

Build:
buildozer android debug

APK:
ls -lh bin/

Copy APK back to Termux:
cp bin/*.apk /data/data/com.termux/files/home/

Then exit Debian:
exit

Open Termux home:
termux-open /data/data/com.termux/files/home/

If Android blocks installation, enable "Install unknown apps" for the app/file manager you use.

Staff login:
Account: su2608
Password: syedu2

This is an educational banking simulation, not production banking software.
