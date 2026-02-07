import customtkinter as ctk
import pandas as pd
from tkinter import messagebox
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class CourtSystemApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("نظام سكرتارية النقض - الهيئة الخماسية الكاملة")
        self.geometry("850x850")
        self.cases_list = []
        
        # القائمة كاملة بالترتيب
        self.judges_names = [
            "نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق", 
            "ماجد ابراهيم", "محسن أبو بكر", "حاتم غراب", 
            "كمال عبد القوى", "محمد منصور", "محمد فؤاد"
        ]
        
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="نظام توزيع طعون الجلسة (الهيئة الخماسية)", font=("Arial", 22, "bold")).pack(pady=20)
        
        frame_top = ctk.CTkFrame(self)
        frame_top.pack(pady=10, padx=20, fill="x")
        self.entry_date = self.create_input(frame_top, "تاريخ الجلسة")

        frame_case = ctk.CTkFrame(self)
        frame_case.pack(pady=10, padx=20, fill="both", expand=True)
        self.entry_no = self.create_input(frame_case, "رقم الطعن")
        self.entry_year = self.create_input(frame_case, "السنة")
        self.entry_appellant = self.create_input(frame_case, "اسم الطاعن")
        self.entry_court = self.create_input(frame_case, "المحكمة المصدر")
        self.entry_charge = self.create_input(frame_case, "التهمة")

        ctk.CTkButton(self, text="1. إضافة الطعن للقائمة", command=self.add_to_list, fg_color="#2b5797", height=45).pack(pady=10)
        ctk.CTkButton(self, text="2. إنشاء ملف التوزيع (+/-)", command=self.generate_excel, fg_color="#1e7145", height=45).pack(pady=10)
        
        ctk.CTkLabel(self, text="الثوابت: نبيل (م1)، سامح (م2)، محمود (م3). ضع (+) للمقرر و (-) للعضوين م4 وم5.", font=("Arial", 12, "italic"), text_color="orange").pack(pady=5)
        ctk.CTkButton(self, text="3. تحويل ومعالجة النتائج النهائية", command=self.process_marks, fg_color="#7e3878", height=50).pack(pady=15)

    def create_input(self, parent, placeholder):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, font=("Arial", 14), height=35, justify="right")
        entry.pack(pady=5, padx=20, fill="x")
        return entry

    def add_to_list(self):
        if not self.entry_no.get():
            messagebox.showwarning("تنبيه", "ادخل رقم الطعن")
            return
        case = {
            'رقم الطعن': self.entry_no.get(), 'السنة': self.entry_year.get(),
            'اسم الطاعن': self.entry_appellant.get(), 'المحكمة المصدر': self.entry_court.get(),
            'التهمة': self.entry_charge.get()
        }
        self.cases_list.append(case)
        messagebox.showinfo("تم", f"تم إضافة الطعن {case['رقم الطعن']}")
        self.clear_fields()

    def clear_fields(self):
        for e in [self.entry_no, self.entry_year, self.entry_appellant, self.entry_court, self.entry_charge]:
            e.delete(0, 'end')

    def generate_excel(self):
        if not self.cases_list: return
        df = pd.DataFrame(self.cases_list)
        for name in self.judges_names: df[name] = ""
        file_name = f"توزيع_{self.entry_date.get()}.xlsx"
        df.to_excel(file_name, index=False)
        os.startfile(file_name)

    def process_marks(self):
        file_name = f"توزيع_{self.entry_date.get()}.xlsx"
        if not os.path.exists(file_name): return
        try:
            df = pd.read_excel(file_name).fillna("")
            final_data = []
            judge_rank = {name: i for i, name in enumerate(self.judges_names)}

            for index, row in df.iterrows():
                case_info = {
                    'رقم الطعن': row['رقم الطعن'], 'السنة': row['السنة'],
                    'الطاعن': row['اسم الطاعن'], 'المحكمة': row['المحكمة المصدر'],
                    'التهمة': row['التهمة'],
                    'المقرر': "",
                    'م1': "نبيل الكشكى", 
                    'م2': "سامح عبد الرحيم", 
                    'م3': "محمود صديق",
                    'م4': "", 'م5': "",
                    'رتبة_المقرر': 999
                }
                
                other_members = []
                for judge in self.judges_names:
                    mark = str(row[judge]).strip()
                    if mark == "+":
                        case_info['المقرر'] = judge
                        case_info['رتبة_المقرر'] = judge_rank[judge]
                    elif mark == "-" and judge not in ["نبيل الكشكى", "سامح عبد الرحيم", "محمود صديق"]:
                        other_members.append(judge)
                
                # إكمال العضو الرابع م4 والخامس م5
                if len(other_members) >= 1: case_info['م4'] = other_members[0]
                if len(other_members) >= 2: case_info['م5'] = other_members[1]
                
                final_data.append(case_info)

            # الترتيب حسب أقدمية المقرر
            final_df = pd.DataFrame(final_data).sort_values(by='رتبة_المقرر')
            final_df = final_df.drop(columns=['رتبة_المقرر'])

            output_file = f"النتائج_النهائية_{self.entry_date.get()}.xlsx"
            final_df.to_excel(output_file, index=False)
            messagebox.showinfo("تم", f"تم التوليد بنجاح للهيئة الخماسية!\nالملف: {output_file}")
            os.startfile(output_file)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {e}")

if __name__ == "__main__":
    app = CourtSystemApp()
    app.mainloop()