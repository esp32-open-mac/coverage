# Automatic init coverage report

The Wi-Fi peripheral needs to be initialized before we can send/receive packets. This is implemented in the binary blobs Espressif distributes, so to have a completely blobless Wi-Fi implementation, we need to implement this initialization ourselves as well. To get a scope of the challenge ahead of us, we used our patched QEMU to trace the execution flow of the Wi-Fi peripheral hardware initialization: every time the proprietary code accesses a memory-mapped register, a stacktrace is generated that logs the whole callstack. This can then be used to see what functions access which hardware registers.

These reports are automatically generated, and viewable on https://esp32-open-mac.be/coverage/
