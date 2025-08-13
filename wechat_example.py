# 使用前要手动验证当前模拟器能正常运行微信并开启必要权限，不会出现死机或者弹出风险限制
from adb_utils import Moniqi
import time 

pos_dict = {"find_button":(803,66),"input_up":(145,66),"input_up_paste":(62,125),"first_result":(145,186),"input_down":(145,1549),"input_down_paste":(46,1482),"emoji_button":(784,1549),"input_down_emoji":(145,1049),"send_button":(854,1547),"wechat_button":(112,1558)}


class WeChat(Moniqi):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.packagename = "com.tencent.mm"
        self.safe_launch_app(self.packagename)

    def reset_wechat(self):
        # 退回到微信主界面
        self.launch_app(self.packagename)
        time.sleep(1)
        self.press_back_until_home()
        self.launch_app(self.packagename)
        self.click(pos_dict["wechat_button"])

    def input_message_up(self,message):
        self.input_text(message,pos_dict["input_up"])

    def into_conversation(self,name):
        # self.launch_app(self.packagename)
        self.click(pos_dict["find_button"])
        self.click(pos_dict["input_up"])
        self.input_message_up(name)
        time.sleep(1)
        self.click(pos_dict["first_result"])
        time.sleep(1)
    
    def input_message_down(self,message):
        # 如果处于语音输入状态，切换为文字输入
        self.click(pos_dict["emoji_button"])
        time.sleep(1)
        self.click(pos_dict["input_down_emoji"])
        self.input_text(message,pos_dict["input_down"])

    def send_message(self,name,message):
        self.reset_wechat()
        self.into_conversation(name)
        self.input_message_down(message)
        self.click(pos_dict["send_button"])

if __name__ == "__main__":

    text = """你好，DocBoJack！根据你的情况（18岁男性，80kg），我们可以制定一个科学、健康的减重计划。以下是具体建议：

### 一、饮食方案（核心原则：高蛋白+适量碳水+低GI）
1. **热量控制**：
   - 建议每日摄入1800-2000大卡（比当前摄入减少300-500大卡）
   - 蛋白质：1.6-2g/kg体重（约130-160g/天）如鸡胸肉/鱼/鸡蛋/豆腐
   - 碳水：3g/kg体重（约240g）选择燕麦/糙米/红薯等
   - 脂肪：25-30%总热量，优选坚果/橄榄油/牛油果
"""
    we = WeChat()
    # we.into_conversation("李信")
    we.send_message("李信",text)
    