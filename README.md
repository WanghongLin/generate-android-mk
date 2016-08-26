# generate-android-mk
A helpful script to create makefiles used in AOSP or NDK development

Installation
------
- Your system must have python installed first
- Copy the script `generate_android_mk.py` to your `PATH`
- If you also want to get bash completion, append the content of `generate_android_mk.bash-completion` to your `~/.bash_completion`

  `$ cat generate_android_mk.bash-completion >> ~/.bash_completion`

Usage
------
An empty share library module will print to stdout if no options supplied.
```makefile
$ generate_android_mk.py

# Auto-generated module by script
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE := 
LOCAL_C_INCLUDES := 
LOCAL_CFLAGS := 
LOCAL_CPPFLAGS := 
LOCAL_LDLIBS := 
LOCAL_SHARED_LIBRARIES := 
LOCAL_STATIC_LIBRARIES := 
LOCAL_PREBUILTS := 
LOCAL_SRC_FILES := 

include $(BUILD_SHARED_LIBRARY)
```
Use option `-t|--type` to specify a template to generate, `exe` for `BUILD_EXECUTABLE`, `apk` for `BUILD_PACKAGE`, etc.

For more help, see
```sh
$ generate_android_mk.py --help
```
