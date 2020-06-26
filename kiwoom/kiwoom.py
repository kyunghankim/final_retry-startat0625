
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *


class kiwoom(QAxWidget):
    def __init__(self): #<- 실행 되기 위한 정의
        super().__init__()

        print('Uiclass안에있는 키움클래스입니다')
        
        ### eventloop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_info_event_loop_2 = None
        #################

        ######### 변수모음
        self.account_num = None
        ##################

        ##### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ############################

        ####### 변수 모음
        self.account_stock_dict ={}


        self.get_ocx_instance() #<- 키움에 레지스트리(KHOPENAPI.KHOpenAPICtrl.1)를 사용하겠다고
                                # 말을 해야 함. 함수 get ocs instance를 정의해서 해결
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() #예수금 가져오는 것
        self.detail_account_mystock() #계좌평가 잔고 내역

# 키움은OCX방식의 컴포넌츠 방식으로 키움 OpenAPI를 실행할 수 있게 함
# 제어가 가능!
    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) #39강
        self.OnReceiveTrdata.connecy(self.trdata_slot)

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop= QEventLoop()
        self.login_event_loop.exec_()


#37강 마지막 자동로그인(오른쪾아래 아이콘, 계좌비밀번호저장 아직 안함)

    def get_account_info(self):
        account_list = self.dynamicCall("GetLogininfo(String)","ACCNO")
        #account_list = self.dynamicCall("GetLogininfo(String)","USER_ID")

        self.account_num = account_list.split(";")[0]

        print("나의계좌번호: %s", self.account_num) #<-계좌번호가져오기

    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()

        #######/38강(로그인)까지
## 39강
    def detail_account_info(self):
        print("예수금 요청 부분")
        self.dynamicCall("SetInputValue(String,String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String,String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String,String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String,String)","조회구분","2")
        self.dynamicCall("CommRqData(String,String,int,String)",
                         "예수금상세현황요청","opw00001","0","2000")#<- 2000:screenNumber
        #screenNumber는 총 200개 까지 요청가능
        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_() #<-loop실행: exec_와 exec는 같은 효과지만 미세가하게 다름(나중에공부)


    def detail_account_mystock(self, sPrevNext='0'):
        print("계좌평가 잔고내역 요청")
        self.dynamicCall("SetInputValue(String,String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String,String)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(String,String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String,String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String,String,int,String)",
                         "계좌평가 잔고내역요청", "opw00018", sPrevNext, "2000")
        self.detail_account_info_event_loop_2 = QEventLoop()
        self.detail_account_info_event_loop_2.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        """
        tr요청을 받는 구역/슬롯
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청 id, tr코드
        :param sRecordName: 사용x
        :param sPrevNext: 다음페이지가 있는지
        :return:
        """
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0,"예수금")
            print("예수금 %s" % int(deposit))

            self.use_money = int(deposit) * self.use_money_percent # 예수금의 50%금액만 사용
            self.use_money = self.use_money / 4 #50%금액의 1/4로 만!



            withdrawal = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0,"출금가능금액")
            print("출금가능금액~ %s" % int(withdrawal))

            self.detail_account_info_event_loop.exit()


        if sRQName == "계좌평가 잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)",
                                               sTrCode, sRQName, 0,"총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총매입금액 %s" % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)",
                                                      sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)

            print("총수익률(%s): %s" % ('%', total_profit_loss_rate_result))

            #GetRepeatCnt: 멀티데이터 조회할때 쓰는것!
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "종목명")
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode,sRQName, i, "종목번호") # 종목앞에 거래소 정보가 알파벳으로!
                code = code.strip()[1:] #strip으로 공백 지우고 1번 다음부터
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "현재가")
                total_paid_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                        sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})



                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity)
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_paid_price = int(total_paid_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_paid_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1

            print("계좌에 가지고이쓴 종목 %s" % len(self.account_stock_dict))

            # 계좌평가잔고내역 시그널!
            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2") # <-위에 정의한 함수에 "2"로 넘어감!!!!
            else:
                self.detail_account_info_event_loop_2.exit()


