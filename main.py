import telebot
from telebot import types
import google.generativeai as genai
import sqlite3
import time
import os
import threading  # أضفنا هذه المكتبة لتعمل في الخلفية


# 1. إعداد الرموز
TOKEN = "8536729769:AAEIQ6RJ8l2KZwYDj7FBLWlYfOyqa30ieCw"
API_KEY = "AIzaSyDqh-4_BkIj7XuflFW9bZUkPATB81mtxMk"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)

# 2. بنك الأسئلة الشامل (31 علوم مع صور + 25 رياضيات)
QUESTIONS_BANK = {
    "العلوم": [
        {"q": "س1: أي من الرسوم البيانية التالية يشير إلى نسبة توزيع اليابسة والماء الصحيحة على سطح الأرض؟", "image": "pictures/ss1 (1).jpeg", "a": "أ"},
        {"q": "س2: بالنظر إلى الرسم الموضح للأجرام السماوية، ماذا يمثل الجرم رقم (2) الذي يدور حول الشمس؟", "image": "pictures/ss2 (2).jpeg", "a": "ب"},
        {"q": "س3: بالنظر إلى الرسم المرفق، هناك خطآن في تمثيل ظل الرجل، هما:", "image": "pictures/ss3 (3).jpeg", "a": "ب"},
        {"q": "س4: أي الأشكال الآتية تشير إلى وضع ظل الشجرة في منتصف النهار عند الساعة 12 تماماً؟", "image": "pictures/ss4 (4).jpeg", "a": "ج"},
        {"q": "س5: عند وضع المكعبات الثلاثة في أواني الماء المتماثلة، في أي إناء سيرتفع مستوى الماء إلى أعلى مستوى؟", "image": "pictures/ss5 (5).jpeg", "a": "ج"},
        {"q": "س6: ماذا يحدث لمكعبات الثلج ذات الأحجام المختلفة عند وضعها في الماء؟", "image": "pictures/ss6 (6).jpeg", "a": "ب"},
        # تكملة الـ 31 سؤال علوم نصية
        {"q": "س7: أي الأجزاء التالية في النبات مسؤولة عن امتصاص الماء؟\nأ) الأوراق\nب) الأزهار\nج) الجذور\nد) الساق", "a": "ج"},
        {"q": "س8: ماذا يحتاج النبات لينمو؟\nأ) الماء والضوء\nب) الظلام فقط\nج) الثلج\nد) العصير", "a": "ب"},
        {"q": "س9: أي مادة تنجذب للمغناطيس؟\nأ) بلاستيك\nب) مسمار حديد\nج) خشب\nد) نحاس", "a": "ب"},
        {"q": "س10: القوة التي تسحب الأجسام للأرض هي:\nأ) المغناطيسية\nب) الجاذبية", "a": "ب"},
        {"q": "س11: تحول الماء من سائل لغاز يسمى:\nأ) تبخر\nب) تجمد\nج) انصهار\nد) تكثف", "a": "أ"},
        {"q": "س12: أي الحواس تخبرك أن القهوة ساخنة دون لمسها؟\nأ) البصر والشم\nب) التذوق", "a": "أ"},
        {"q": "س13: تعيش الأسماك في الماء وتتنفس بواسطة:\nأ) الرئتين\nب) الخياشيم", "a": "ب"},
        {"q": "س14: أي كوكب هو الأقرب للشمس؟\nأ) المريخ\nب) عطارد", "a": "ب"},
        {"q": "س15: ما العضو الذي نستخدمه للتفكير؟\nأ) القلب\nب) الدماغ", "a": "ب"},
        {"q": "س16: أي كائن يبيض ولا يلد؟\nأ) القطة\nب) الدجاجة", "a": "ب"},
        {"q": "س17: ما فائدة الهيكل العظمي؟\nأ) الهضم\nب) الحماية والدعم", "a": "ب"},
        {"q": "س18: لماذا نرى القمر مضيئاً؟\nأ) يعكس ضوء الشمس\nب) هو نفسه مضيء", "a": "أ"},
        {"q": "س19: الحالة التي ليس لها شكل ثابت هي:\nأ) الصلبة\nب) السائلة", "a": "ب"},
        {"q": "س20: مصدر الضوء الرئيسي للأرض هو:\nأ) القمر\nب) الشمس", "a": "ب"},
        {"q": "س21: تهاجر الطيور بحثاً عن:\nأ) اللعب\nب) الدفء والغذاء", "a": "ب"},
        {"q": "س22: كيف نحمي البيئة؟\nأ) حرق النفايات\nب) إعادة التدوير", "a": "ب"},
        {"q": "س23: أي جزء ينقل الغذاء لباقي النبات؟\nأ) الجذور\nب) الساق", "a": "ب"},
        {"q": "س24: أي من هذه الأشياء شفاف؟\nأ) الحديد\nب) الزجاج", "a": "ب"},
        {"q": "س25: الوحدة المستخدمة لقياس الكتلة هي:\nأ) المتر\nب) الكيلوغرام", "a": "ب"},
        {"q": "س26: ماذا يحدث عند تجمد الماء؟\nأ) يتبخر\nب) يصبح صلباً", "a": "ب"},
        {"q": "س27: أي الحيوانات التالية مفترس؟\nأ) الأرنب\nب) الأسد", "a": "ب"},
        {"q": "س28: كم فصلاً في السنة؟\nأ) 3 فصول\nب) 4 فصول", "a": "ب"},
        {"q": "س29: أي مما يلي يمثل دورة حياة نبات؟\nأ) بذرة ثم بادرة ثم نبات\nب) فراشة ثم بيضة", "a": "أ"},
        {"q": "س30: لماذا يلبس رائد الفضاء بدلة خاصة؟\nأ) للزينة\nب) للحماية وتوفير الأكسجين", "a": "ب"},
        {"q": "س31: أين نجد الماء المالح؟\nأ) الأنهار\nب) البحار والمحيطات", "a": "ب"}
    ],
    "الرياضيات": [
        {"q": "س1: ما ناتج جمع 150 + 250؟\nأ) 300\nب) 400\nج) 500\nد) 350", "a": "ب"},
        {"q": "س2: ناتج ضرب 6 × 7 هو:\nأ) 42\nب) 48\nج) 36\nد) 49", "a": "أ"},
        {"q": "س3: أي كسر يمثل الربع؟\nأ) 1/2\nب) 1/3\nج) 1/4\nد) 3/4", "a": "ج"},
        {"q": "س4: حديقة مربعة طول ضلعها 5م، مساحتها هي:\nأ) 10 م2\nب) 20 م2\nج) 25 م2\nد) 15 م2", "a": "ج"},
        {"q": "س5: كم دقيقة في ساعة ونصف؟\nأ) 60\nب) 90\nج) 80\nد) 100", "a": "ب"},
        {"q": "س6: أي عدد هو عدد زوجي؟\nأ) 11\nب) 23\nج) 44\nد) 57", "a": "ج"},
        {"q": "س7: ناتج قسمة 20 ÷ 4 هو:\nأ) 5\nب) 4\nج) 6\nد) 10", "a": "أ"},
        {"q": "س8: القيمة المنزلية للرقم 3 في العدد 4352 هي:\nأ) 3\nب) 30\nج) 300\nد) 3000", "a": "ج"},
        {"q": "س9: أي الزوايا قياسها 90 درجة؟\nأ) الحادة\nب) القائمة\nج) المنفرجة\nد) المستقيمة", "a": "ب"},
        {"q": "س10: ناتج طرح 100 - 45 هو:\nأ) 65\nب) 55\nج) 45\nد) 35", "a": "ب"},
        {"q": "س11: كم عدد الأضلاع في الشكل الخماسي؟\nأ) 4\nب) 5\nج) 6\nد) 3", "a": "ب"},
        {"q": "س12: أي الأعداد التالية هو الأكبر؟\nأ) 4050\nب) 4500\nج) 4005\nد) 4550", "a": "د"},
        {"q": "س13: إذا كان مع أحمد 10 دنانير واشترى قصة بـ 3 دنانير، كم تبقى معه؟\nأ) 5\nب) 6\nج) 7\nد) 8", "a": "ج"},
        {"q": "س14: ناتج ضرب 10 × 15 هو:\nأ) 105\nب) 150\nج) 200\nد) 115", "a": "ب"},
        {"q": "س15: كم سم في 3 أمتار؟\nأ) 30\nب) 300\nج) 3000\nد) 13", "a": "ب"},
        {"q": "س16: ما هو نصف العدد 50؟\nأ) 20\nب) 25\nج) 30\nد) 15", "a": "ب"},
        {"q": "س17: عدد أيام الأسبوع هو:\nأ) 5\nب) 6\nج) 7\nد) 8", "a": "ج"},
        {"q": "س18: أي كسر يكافئ 2/4؟\nأ) 1/2\nب) 1/3\nج) 1/4\nد) 1/5", "a": "أ"},
        {"q": "س19: مثلث أطوال أضلاعه متساوية يسمى:\nأ) مختلف الأضلاع\nب) متساوي الأضلاع\nج) قائم\nد) منفرج", "a": "ب"},
        {"q": "س20: ناتج جمع 12.5 + 2.5 هو:\nأ) 14\nب) 15\nج) 14.5\nد) 16", "a": "ب"},
        {"q": "س21: ما هو العدد التالي في النمط: 10، 20، 30، ...؟\nأ) 35\nب) 40\nج) 50\nد) 45", "a": "ب"},
        {"q": "س22: كم ثانية في الدقيقة الواحدة؟\nأ) 30\nب) 60\nج) 100\nد) 120", "a": "ب"},
        {"q": "س23: أي من هذه الأعداد يقبل القسمة على 5؟\nأ) 12\nب) 24\nج) 35\nد) 41", "a": "ج"},
        {"q": "س24: ما هو ناتج 0 × 500؟\nأ) 500\nب) 50\nج) 0\nد) 1", "a": "ج"},
        {"q": "س25: ما اسم الشكل الذي له 6 أوجه مربعة متطابقة؟\nأ) الهرم\nب) المكعب\nج) الأسطوانة\nد) المخروط", "a": "ب"}
    ]
}

def init_db():
    conn = sqlite3.connect('timss_jordan_pro.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS progress 
                      (user_id INTEGER PRIMARY KEY, subject TEXT, q_num INTEGER, tries INTEGER, score INTEGER)''')
    conn.commit()
    conn.close()

def get_progress(uid):
    conn = sqlite3.connect('timss_jordan_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT subject, q_num, tries, score FROM progress WHERE user_id=?", (uid,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, 1, 0, 0)

def set_progress(uid, sub, q, t, s):
    conn = sqlite3.connect('timss_jordan_pro.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO progress VALUES (?, ?, ?, ?, ?)", (uid, sub, q, t, s))
    conn.commit()
    conn.close()

init_db()

def send_question(uid, sub, q_num):
    idx = q_num - 1
    q_data = QUESTIONS_BANK[sub][idx]
    text = q_data['q']
    
    # خيارات ثابتة تظهر تحت صور العلوم فقط
    img_options = "\n\nأ) الخيار الأول\nب) الخيار الثاني\nج) الخيار الثالث\nد) الخيار الرابع"
    
    if 'image' in q_data and os.path.exists(q_data['image']):
        with open(q_data['image'], 'rb') as photo:
            bot.send_photo(uid, photo, caption=text + img_options)
    else:
        bot.send_message(uid, text)

@bot.message_handler(commands=['start', 'menu'])
def start(message):
    uid = message.chat.id
    set_progress(uid, None, 1, 0, 0)
    btn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn.add("العلوم 🧬", "الرياضيات 📐")
    bot.send_message(uid, "📊 مرحباً بك معلمنا في تحدي TIMSS الأردن\nاختر المادة للبدء واستمتع بالصور:", reply_markup=btn)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    uid = message.chat.id
    text = message.text.strip()
    sub, q_num, tries, score = get_progress(uid)

    if sub is None:
        if "العلوم" in text: sub = "العلوم"
        elif "الرياضيات" in text: sub = "الرياضيات"
        else: return
        set_progress(uid, sub, 1, 0, score)
        send_question(uid, sub, 1)
        return

    map_answers = {"1":"أ", "2":"ب", "3":"ج", "4":"د", "a":"أ", "b":"ب", "c":"ج", "d":"د"}
    final_input = map_answers.get(text, text)
    correct = QUESTIONS_BANK[sub][q_num-1]['a']

    if final_input == correct:
        bot.send_message(uid, "أحسنت ✅ إجابة صحيحة!")
        if q_num < len(QUESTIONS_BANK[sub]):
            set_progress(uid, sub, q_num + 1, 0, score + 1)
            send_question(uid, sub, q_num + 1)
        else:
            bot.send_message(uid, f"🎉 مبروك! أنهيت كافة أسئلة {sub}.\nمجموع نقاطك: {score + 1}")
            # العودة للقائمة الرئيسية
            set_progress(uid, None, 1, 0, 0)
            btn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn.add("العلوم 🧬", "الرياضيات 📐")
            bot.send_message(uid, "اختر مادة أخرى أو أعد الاختبار:", reply_markup=btn)
    else:
        tries += 1
        if tries < 2:
            set_progress(uid, sub, q_num, tries, score)
            bot.send_message(uid, "محاولة خاطئة 🔄 حاول مرة ثانية.")
        else:
            bot.send_message(uid, f"الإجابة الصحيحة هي ({correct}).")
            try:
                p = f"اشرح لطفل صف رابع ببساطة لماذا الإجابة هي {correct} لهذا السؤال: {QUESTIONS_BANK[sub][q_num-1]['q']}"
                res = model.generate_content(p)
                bot.send_message(uid, "💡 شرح المعلم:\n" + res.text)
            except: pass
            
            if q_num < len(QUESTIONS_BANK[sub]):
                set_progress(uid, sub, q_num + 1, 0, score)
                send_question(uid, sub, q_num + 1)
            else:
                bot.send_message(uid, "انتهت أسئلة هذا القسم.")
                start(message)

while True:try:
            print("✅ النسخة الاحترافية النهائية تعمل الآن.. مع دعم الخيارات تحت الصور!")
        except Exception as e:
            print(f"خطأ في الطباعة: {e}")

        # ----------------- ميزة التذكير كل 5 دقائق -----------------
def reminder_thread():
    """هذه الدالة تعمل في الخلفية لإرسال تذكير كل 5 دقائق"""
    while True:
        try:
            time.sleep(300)  # الانتظار لمدة 300 ثانية (5 دقائق)
            for chat_id in list(user_status.keys()):
                try:
                    bot.send_message(chat_id, "💡 تذكير: يا بطل، لا تنسى إكمال اختبارك! أرسل إجابتك للسؤال المتبقي.")
                except Exception:
                    pass  # لتفادي توقف السيرفر إذا قام طالب بحظر البوت
        except Exception as e:
            print(f"Error in reminder thread: {e}")
            time.sleep(10) # انتظار بسيط قبل المحاولة مرة أخرى في حال حدوث خطأ عام
# بدء تشغيل التذكير في مسار منفصل (Thread)
t = threading.Thread(target=reminder_thread)
t.daemon = True
t.start()
# --------------------------------------------------------
        bot.polling(none_stop=True)
    except: time.sleep(5)


