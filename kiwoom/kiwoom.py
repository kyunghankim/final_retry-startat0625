
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *


class kiwoom(QAxWidget):
    def __init__(self): #<- 실행 되기 위한 정의
        super().__init__()

        print('Uiclass안에있는 키움클래스입니다')
        
        ### eventloop 모음
        self.login_event_loop = None
        #################

        ######### 변수모음
        self.account_num = None
        ##################

        self.get_ocx_instance() #<- 키움에 레지스트리(KHOPENAPI.KHOpenAPICtrl.1)를 사용하겠다고
                                # 말을 해야 함. 함수 get ocs instance를 정의해서 해결
        self.event_slots()
        self.signal_login_commConnect()
        self.get_account_info()

# 키움은OCX방식의 컴포넌츠 방식으로 키움 OpenAPI를 실행할 수 있게 함
# 제어가 가능!
    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop= QEventLoop()
        self.login_event_loop.exec_()

    def login_slot(self,errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

#37강 마지막 자동로그인(오른쪾아래 아이콘, 계좌비밀번호저장 아직 안함)

    def get_account_info(self):
        account_list = self.dynamicCall("GetLogininfo(String)","ACCNO")
        #account_list = self.dynamicCall("GetLogininfo(String)","USER_ID")

        self.account_num = account_list.split(";")[0]

        print("나의계좌번호: %s", self.account_num)


        #######/38강(로그인)까지
