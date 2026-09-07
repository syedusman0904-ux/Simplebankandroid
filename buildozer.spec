[app]
title = Simple Bank
package.name = simplebank
package.domain = org.syed
source.dir = .
source.include_exts = py,json,kv
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 0

[android]
android.api = 35
android.minapi = 23
android.ndk = 28b
android.accept_sdk_license = True
