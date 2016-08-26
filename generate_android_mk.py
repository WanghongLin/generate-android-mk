#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple script to generate makefiles used in AOSP
# 
# Copyright 2016 Wanghong Lin
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generate Android makefiles

import os
import sys
import getopt
import re

OPT_TEMPLATES = {}
OPT_TEMPLATES['exe'] = 'include $(BUILD_EXECUTABLE)'
OPT_TEMPLATES['shared'] = 'include $(BUILD_SHARED_LIBRARY)'
OPT_TEMPLATES['static'] = 'include $(BUILD_STATIC_LIBRARY)'
OPT_TEMPLATES['pshared'] = 'include $(PREBUILT_SHARED_LIBRARY)'
OPT_TEMPLATES['pstatic'] = 'include $(PREBUILT_STATIC_LIBRARY)'
OPT_TEMPLATES['apk'] = 'include $(BUILD_PACKAGE)'
OPT_TEMPLATES['papk'] = 'include $(BUILD_PREBUILT)'
OPT_TEMPLATES['java'] = 'include $(BUILD_STATIC_JAVA_LIBRARY)'
OPT_TEMPLATES['top'] = 'include $(call all-subdir-makefiles)'

g_scan_sources_list = ''
g_scan_exclude_pattern = ''

def show_usage():
  """TODO: Docstring for usage.
  :returns: TODO

  """
  print "Usage: " + sys.argv[0] + " [OPTIONS...] [a-list-of-source-files]"
  print "\t-t|--type     Specify module type, one of the 'exe', 'shared', 'static', 'pshared', 'pstatic', 'apk', 'papk', 'java', 'top'"
  print "\t              They are equivalent to BUILD_EXECUTABLE, BUILD_SHARED_LIBRRY, BUILD_STATIC_LIBRARY, PREBUILT_SHARED_LIBRARY"
  print "\t              PREBUILT_STATIC_LIBRARY, BUILD_PACKAGE, BUILD_PREBUILT, BUILD_STATIC_JAVA_LIBRARY, Top level makefile call"
  print "\t              all subdir makefiles"
  print "\t-m|--module   The name of module, equivalent to LOCAL_MODULE_NAME"
  print "\t-i|--include  An optional list of paths, relative to the NDK *root* directory, which will be appended to"
  print "\t              the include search path when compiling all sources (C, C++ and Assembly), LOCAL_C_INCLUDES"
  print "\t-f|--cflags   An optional set of compiler flags that will be passed when building C *and* C++ source files."
  print "\t              This equivalent to LOCAL_CFLAGS"
  print "\t-F|--cppflags An optional set of compiler flags that will be passed when building C++ source files *only*."
  print "\t              This is equal to LOCAL_CPPFLAGS or LOCAL_CXXFLAGS."
  print "\t-l|--ldlibs   The list of additional linker flags to be used when building your module, without -l prefix, e.g log z"
  print "\t-d|--shared   The list of shared libraries *modules* this module depends on at runtime. LOCAL_SHARED_LIBRARIES"
  print "\t-D|--static   The list of static libraries modules (built with BUILD_STATIC_LIBRARY) that should be linked to this module."
  print "\t              This only makes sense in shared library modules. LOCAL_STATIC_LIBRARIES"
  print "\t-p|--prebuilt Prebuilt module(a module build with PREBUILT_SHARED_LIBRARY or PREBUILT_STATIC_LIBRARY) "
  print "\t              that this module depends on"
  print "\t-j|--java     The list of static java libraries this module depends on, LOCAL_STATIC_JAVA_LIBRARIES"
  print "\t-c|--certificate"
  print "\t              Path of the certificate to sign the apk, default to 'platform'"
  print "\t-O|--output   The output file to write, default is stdout"
  print "\t-o|--override Android.mk will be override if specifying this option, this is the default behavior"
  print "\t-a|--append   Use it if you want your generated module to be appended in the existing Android.mk"
  print "\t-s|--scan     Specify a directory to scan sources (.c,.cpp,.cxx) and append to LOCAL_SRC_FILES."
  print "\t              No need for java, usualy use $(call all-subdir-java-files) to get all java sources"
  print "\t-r|--recursive"
  print "\t              Recusrively scan source directory"
  print "\t-e|--exclude  A exclude regular expression pattern for file scaning"
  print "\t-A|--abi      A comma separated ABIs, e.g armeabi,armeabi-v7a,arm64-v8a,x86,x86_64,mips,mips64"
  print "\t              Use 'all' to support all ABIs, this is the default behavior, this option will write to Appliclation.mk"
  print "\t-P|--platform The name of the target android platform, e.g android-16, This option will be written to Application.mk"
  print "\t              'APP_PIE := false' will be automatically added to Application.mk if target platform lower than android-16"
  print "\t-v|--verbose  Set if runing in verbose mode, 1 or 0"
  print "\t-h|--help     Show this help.\n"
  sys.exit(0)
  pass

def find_sources(directory):
  """TODO: Docstring for find_sources.

  :directory: TODO
  :returns: TODO

  """
  global g_scan_sources_list
  global g_scan_exclude_pattern
  for f in os.listdir(directory):
    p = os.path.join(directory, f)
    if os.path.isdir(p):
      find_sources(p)
    else:
      if p.endswith('.c') or p.endswith('.cpp') or p.endswith('.cxx'):
        if len(g_scan_exclude_pattern) == 0 or (len(g_scan_exclude_pattern) > 0 and not re.search(g_scan_exclude_pattern, p)):
          g_scan_sources_list += p + ' \\\n'
  pass

def add_scan_sources(dir_to_scan, recursive):
  """TODO: Docstring for add_scan_sources.

  :source_dir: TODO
  :content: TODO
  :recursive: TODO
  :returns: TODO

  """
  if recursive:
    find_sources(dir_to_scan)
  else:
    global g_scan_sources_list
    global g_scan_exclude_pattern
    for f in os.listdir(dir_to_scan):
      if f.endswith('.c') or f.endswith('.cpp') or f.endswith('.cxx'):
        p = os.path.join(dir_to_scan, f)
        if len(g_scan_exclude_pattern) == 0 or (len(g_scan_exclude_pattern) > 0 and not re.search(g_scan_exclude_pattern, p)):
          g_scan_sources_list += p + ' \\\n'

def main():
  """TODO: Docstring for main.
  :returns: TODO

  """
  try:
    # Short option syntax: "hv:"
    # Long option syntax: "help" or "verbose="
    opts, args = getopt.getopt(sys.argv[1:], "hoars:e:v:t:m:i:f:F:l:d:D:j:p:c:O:A:P:", ["help", "override", "append", "recursive", 
      "scan=", "exclude=", "verbose=", "type=", "module=", "include=", "cflags=", "cppflags=", "ldlibs=", "shared=", "static=", 
      "java=", "prebuilt=", "certificate=", "output=", "abi=", "platform="])
  
  except getopt.GetoptError, err:
    # Print debug info
    print str(err)
    sys.exit(0);
  
  verbose = 0
  opt_override = True
  opt_scan_dir = ''
  opt_scan_recursive = False
  opt_scan_exclude = ''
  opt_module = ''
  opt_template = ''
  opt_include = ''
  opt_java = ''
  opt_cflags = ''
  opt_ldlibs = ''
  opt_cppflags = ''
  opt_shared = ''
  opt_static = ''
  opt_prebuilts = ''
  opt_certificate = 'platform'
  opt_output = ''
  opt_abis = ''
  opt_platform = ''
  opt_src_list = sys.argv[1:]

  for option, argument in opts:
    if option in ("-h", "--help"):
      show_usage()
    elif option in ("-A", "--abi"):
      opt_abis = argument.replace(',', ' ')
    elif option in ("-P", "--platform"):
      opt_platform = argument
    elif option in ("-e", "--exclude"):
      global g_scan_exclude_pattern
      g_scan_exclude_pattern = argument
    elif option in ("-s", "--scan"):
      opt_scan_dir = argument
    elif option in ("-r", "--recursive"):
      opt_scan_recursive = True
    elif option in ("-O", "--output"):
      opt_output = argument
    elif option in ("-c", "--certificate"):
      opt_certificate = argument
    elif option in ("-j", "--java"):
      opt_java = argument
    elif option in ("-D", "--static"):
      opt_static = argument
    elif option in ("-d", "--shared"):
      opt_shared = argument
    elif option in ("-l", "--ldlibs"):
      opt_ldlibs = argument
    elif option in ("-F", "--cppflags"):
      opt_cppflags = argument
    elif option in ("-f", "--cflags"):
      opt_cflags = argument
    elif option in ("-i", "--include"):
      opt_include = argument
    elif option in ("-v", "--verbose"):
      verbose = argument
    elif option in ("-a", "--append"):
      opt_override = False
    elif option in ("-o", "--override"):
      opt_override = True
    elif option in ("-t", "--type"):
      opt_template = argument
    elif option in ("-m", "--module"):
      opt_module = argument
    elif option in ('-p', '--prebuilt'):
      opt_prebuilts = argument
    else:
      pass
    
    if option in opt_src_list:
      opt_src_list.remove(option)
    if argument in opt_src_list:
      opt_src_list.remove(argument)
  
  if not opt_template:
    if verbose == 1:
      print "No type specifying, use the default BUILD_SHARED_LIBRARY"
    opt_template = 'shared'
  
  if not opt_module and verbose == 1:
    print "No module name, leave it empty"
    opt_module = ''

  if not opt_template in OPT_TEMPLATES:
    print 'Invalid template type, should be one of ' + str(OPT_TEMPLATES.keys())
    print 'Use -h|--help option to get more helps'
    sys.exit()

  content = "\n# Auto-generated module by script\n"
  content += "LOCAL_PATH := $(call my-dir)\n"
  content += "include $(CLEAR_VARS)\n\n"

  if opt_template == 'apk':
    content += "LOCAL_PACKAGE_NAME := " + opt_module + "\n"
  elif opt_template == 'top':
    pass
  else:
    content += "LOCAL_MODULE := " + opt_module + "\n"

  if opt_template == 'shared' or opt_template == 'static' or opt_template == 'exe':
    content += "LOCAL_C_INCLUDES := " + opt_include + "\n"
    content += "LOCAL_CFLAGS := " + opt_cflags + "\n"
    content += "LOCAL_CPPFLAGS := " + opt_cppflags + "\n"
    content += "LOCAL_LDLIBS := "

    if len(opt_ldlibs) > 0:
      for l in opt_ldlibs.split(' '):
        content += '-l' + l + ' '

    content += "\n"
    content += "LOCAL_SHARED_LIBRARIES := " + opt_shared + "\n"
    content += "LOCAL_STATIC_LIBRARIES := " + opt_static + "\n"
    content += "LOCAL_PREBUILTS := " + opt_prebuilts + "\n"

  if opt_template == 'apk' or opt_template == 'java':
    content += "LOCAL_SRC_FILES := $(call all-subdir-java-files)\n"
    content += "LOCAL_STATIC_JAVA_LIBRARIES := " + opt_java + "\n"
  elif opt_template == 'papk':
    content += "LOCAL_SRC_FILES := $(LOCAL_MODULE).apk\n"
    content += "LOCAL_MODULE_CLASS := APPS\n"
    content += "LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)\n"
  elif opt_template == 'top':
    pass
  else:
    content += "LOCAL_SRC_FILES := "

    if len(opt_scan_dir) > 0 and os.path.isdir(opt_scan_dir):
      add_scan_sources(opt_scan_dir, opt_scan_recursive)
      global g_scan_sources_list
      content += g_scan_sources_list

    if len(opt_src_list) > 0:
      for s in opt_src_list:
        content += s + ' '

    content += "\n"
  
  if opt_template == 'apk':
    content += "LOCAL_CERTIFICATE := " + opt_certificate + "\n"

  content += "\n" + OPT_TEMPLATES.get(opt_template) + "\n"

  if len(opt_output) > 0:
    f = None
    if opt_override:
      f = open(opt_output, "w+")
    else:
      f = open(opt_output, "a+")
    f.write(content)
    f.close()
  else:
    print content

  if (len(opt_abis) > 0 or len(opt_platform) > 0) and len(opt_output) > 0:
    f = open(os.path.join(os.path.dirname(opt_output), 'Application.mk'), 'w+')
    app = ''
    if len(opt_abis) > 0:
      app += "APP_ABI := " + opt_abis + "\n"
    if len(opt_platform) > 0:
      match = re.search('android-(\d+)', opt_platform)
      if match:
        app += "APP_PLATFORM := " + opt_platform + "\n"
        # disable PIE when build executable prior android-16
        if match.group(1) < 16 and opt_template == 'exe':
          app += "APP_PIE := false\n"
    f.write(app)
    f.close()

  pass

if __name__ == "__main__":
  main()
