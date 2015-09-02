# coding=gbk

# Android4.X��OS X10.10.X�ϱ���ʱ������AndroidԴ�������ԭ���޷�ֱ����ȷ�ı��룬
# ��Ҫ�޸�һЩ���ò�����ȷ�ı��룬����ű����������Զ����޸�AndroidԴ������ã��޸���ɺ�
# ����ʹAndroid4.X��OS X10.10.X����ȷ���롣

# ��Ҫ˵�����ǣ�Android4.X������ʹ�õ�jdk������jdk6�����������ĵ�����û��jdk6����ô�����ء�

'''

�ű�����˵����
-d����ѡ������ָ��AndroidԴ���Ŀ¼��������ű���AndroidԴ���Ŀ¼����ô���Բ����������������������������������
-j����ѡ������jdk6��java home·���������ĵ����ϵ�jdk����������jdk6����ô���Բ��������ѡ�
    ����Ҫô�������������Ҫô���Լ�����jdk6�Ļ���������ע�⣺���ű����õĻ�������ֻ�ڵ�ǰ�ն�����������Ч��
'''

__author__ = 'buwai'

import os
import sys
import getopt
import commands
import shutil
import logging
import re

class MacAndroidBuildEnv:
    __androidRoot = None
    __javaHome = None
    __hostMakeFilePath = None
    __macSdkVersion = None
    __jniGeneratorPath = None

    def setAndroidRoot(self, androidRoot):
        self.__androidRoot = androidRoot
        self.__hostMakeFilePath = self.__androidRoot + r"/build/core/combo/HOST_darwin-x86.mk"

        # ���ԭ�����ڣ���ԭ��������ΪHOST_darwin-x86.mk���ļ�
        origHostMakeFilePath = self.__hostMakeFilePath + ".orig"
        if (os.path.isfile(origHostMakeFilePath)):
            shutil.copy(origHostMakeFilePath, self.__hostMakeFilePath)

        # ��õ�ǰAndroidԴ��֧�ֵ�mac sdk�汾
        macSdkVersionSupported = self.__getMacSdkVersionSupported(buildEnv.getHostMakeFilePath())
        #print("macSdkVersionSupported: %s" % macSdkVersionSupported)
        # get mac sdk version
        status, macSdkVersionsInstalled = commands.getstatusoutput(r'xcodebuild -showsdks | grep macosx | sort | sed -e "s/.*macosx//g"')
        macSdkVersionsInstalled = macSdkVersionsInstalled.splitlines();
        # ����mac���Ƿ���AndroidԴ����֧�ֵ�sdk�汾
        for sdkVersion in macSdkVersionSupported:
            if sdkVersion in macSdkVersionsInstalled:
                self.__macSdkVersion = sdkVersion
                break;

        # �ж��Ƿ��ҵ����ʵ�SDK�汾
        if (None == self.__macSdkVersion):
            self.__macSdkVersion = macSdkVersionsInstalled[0]
        #print(self.__macSdkVersion)
        #print("status=%d result=%s" % (status, macSdkVersionsInstalled))

        # ���ԭ�����ڣ���ԭ��������Ϊjni_generator.py���ļ�
        self.__jniGeneratorPath = self.__androidRoot + r"/external/chromium_org/base/android/jni_generator/jni_generator.py"
        origJniGeneratorPath = self.__jniGeneratorPath + ".orig"
        if (os.path.isfile(origJniGeneratorPath)):
            shutil.copy(origJniGeneratorPath, self.__jniGeneratorPath)

    def setJavaHome(self, javaHome):
        javaBin = javaHome + os.sep + "bin" + os.sep + "java"
        result = commands.getoutput(javaBin + " -version")
        result = result.split('\n')[0]
        pattern = re.compile(r'java version "1\.6')
        match = pattern.match(result)
        if (None == match):
            raise Exception("java home not java6 home")
        self.__javaHome = javaHome

    def getJavaHome(self):
        return self.__javaHome

    def getHostMakeFilePath(self):
        return self.__hostMakeFilePath

    def getMacSdkVersion(self):
        return self.__macSdkVersion

    def getJniGeneratorPath(self):
        return self.__jniGeneratorPath

    # ��õ�ǰAndroidԴ��֧�ֵ�mac sdk�汾
    # ��óɹ����򷵻�AndroidԴ��֧�ֵ�mac sdk�汾�б����ʧ�ܣ��򷵻�None
    def __getMacSdkVersionSupported(self, filePath):
        result=None
        with open(filePath) as file:
            while 1:
                line = file.readline()
                index = line.find(r"mac_sdk_versions_supported :=")
                if (0 == index):
                    line = line[len(r"mac_sdk_versions_supported :="):].strip()
                    result = line.split(" ")
                    break
                if not line:
                    break
                pass # do something

        return result

class MacAndroidBuildEnvImpl:
    __macBuildEnv=None

    def __init__(self, macBuildEnv):
        self.__macBuildEnv = macBuildEnv

    def process(self):
        # ����java6�Ļ�������
        self.setJava6Env()
        # �޸�HOST_darwin-x86.mk
        self.__modifyHostMakeFile()
        # �޸�jni_generator.py�ļ�
        self.__modifyJniGenerator()

    '''
    ����java6�Ļ�������
    '''
    def setJava6Env(self):
        javaHome = self.__macBuildEnv.getJavaHome()
        if (None != javaHome):
            # ����java6�Ļ�������
            os.environ['JAVA_HOME'] = javaHome;
            os.environ['PATH'] = os.environ['JAVA_HOME'] + os.sep + "bin:" + os.environ['PATH']

    '''
    �޸�HOST_darwin-x86.mk
    '''
    def __modifyHostMakeFile(self):
        hostMakeFilePath = self.__macBuildEnv.getHostMakeFilePath()
        origHostMakeFilePath = hostMakeFilePath + ".orig"   # ���ڱ���ԭ��
        newHostMakeFilePath = hostMakeFilePath + ".new"
        macSdkVersion = self.__macBuildEnv.getMacSdkVersion()

        # ���û�б���ԭ�������ȱ���ԭ��
        if (False == os.path.isfile(origHostMakeFilePath)):
            shutil.copy(hostMakeFilePath, origHostMakeFilePath)

        with open(hostMakeFilePath, 'r') as f:
            with open(newHostMakeFilePath, 'w') as g:
                for line in f.readlines():
                    index = line.find(r"mac_sdk_versions_supported :=")
                    if (0 == index):
                        line = r"mac_sdk_versions_supported := " + macSdkVersion + "\n"
                    elif (0 == line.find(r"ifeq ($(mac_sdk_version),10.8)")):
                        line = r"ifeq ($(mac_sdk_version)," + macSdkVersion + r")" + "\n"
                    g.write(line)

        # �����ļ�����ΪHOST_darwin-x86.mk
        shutil.move(newHostMakeFilePath, hostMakeFilePath)

    '''
    �޸�jni_generator.py�ļ�
    '''
    def __modifyJniGenerator(self):
        filePath = self.__macBuildEnv.getJniGeneratorPath()
        origFilePath = filePath + ".orig"
        newFilePath = filePath + ".new"

        # ���û�б���ԭ�������ȱ���ԭ��
        if (False == os.path.isfile(origFilePath)):
            shutil.copy(filePath, origFilePath)

        with open(filePath, 'r') as f:
            with open(newFilePath, 'w') as g:
                for line in f.readlines():
                    if (0 == line.find(r"class JNIFromJavaSource(object):")):
                        g.write("import platform\n")
                        g.write(line)
                    else:
                        index = line.find(r"p = subprocess.Popen(args=['cpp', '-fpreprocessed'],")
                        if (-1 != index):
                            spaces = line[0:index]
                            g.write(spaces + r"system = platform.system()" + "\n")
                            g.write(spaces + r"if system == 'Darwin':" + "\n")
                            g.write(spaces + "    " + r"cpp_args = ['cpp']" + "\n")
                            g.write(spaces + "else:\n")
                            g.write(spaces + "    " + r"cpp_args = ['cpp', '-fpreprocessed']" + "\n")
                            g.write(spaces + r"p = subprocess.Popen(args=cpp_args," + "\n")
                        else:
                            g.write(line)

        # �����ļ�����Ϊjni_generator.py
        shutil.move(newFilePath, filePath)

def usage():
    print("Usage:%s" % sys.argv[0])
    print("-h")
    print("[-d <android src root>] [-j <java home>]")

try:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    logging.StreamHandler(sys.stdout)
    logging.info("------ start process ------")

    androidRoot = None
    javaHome = None
    # �����н���
    options, remainder = getopt.getopt(sys.argv[1:], 'd:j:')
    for opt, arg in options:
        if opt in ("-h"):
            usage()
            sys.exit(1)
        elif opt in ("-d"):
            androidRoot = arg
        elif opt in ("-j"):
            javaHome = arg
        else:
            usage()
            sys.exit(1)

    if (None == androidRoot):
        androidRoot = os.path.split(os.path.realpath(__file__))[0]

    buildEnv = MacAndroidBuildEnv()
    buildEnv.setAndroidRoot(androidRoot)
    if (None != javaHome):
        buildEnv.setJavaHome(javaHome)

    buildEnvImpl = MacAndroidBuildEnvImpl(buildEnv)
    buildEnvImpl.process()

    logging.info("------ end process ------")
except Exception as err:
    print 'ERROR:', err
    sys.exit(1)