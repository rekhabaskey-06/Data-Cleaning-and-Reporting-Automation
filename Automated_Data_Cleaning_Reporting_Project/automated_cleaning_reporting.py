from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_FILE='raw_student_data.csv'
OUT=Path('output'); OUT.mkdir(exist_ok=True)
df=pd.read_csv(INPUT_FILE)
original_rows, original_cols=len(df), len(df.columns)
df.isna().sum().rename_axis('Column').reset_index(name='Missing_Count').to_csv(OUT/'missing_values_before.csv',index=False)
dups=int(df.duplicated().sum())
df['Student']=df['Student'].astype(str).str.strip().str.title()
mp={'cse':'CSE','computer science':'CSE','ece':'ECE','me':'ME','mechanical':'ME'}
df['Department']=df['Department'].astype(str).str.strip().str.lower().map(mp).fillna(df['Department'].astype(str).str.strip().str.upper())
df['Marks']=pd.to_numeric(df['Marks'],errors='coerce')
df['Attendance']=pd.to_numeric(df['Attendance'],errors='coerce')
missing_marks=int(df['Marks'].isna().sum()); missing_att=int(df['Attendance'].isna().sum())
df['Marks']=df['Marks'].fillna(df['Marks'].median()); df['Attendance']=df['Attendance'].fillna(df['Attendance'].median())
df=df.drop_duplicates().reset_index(drop=True)
df['Marks']=df['Marks'].clip(0,100); df['Attendance']=df['Attendance'].clip(0,100)
def grade(x):
    return 'A+' if x>=90 else 'A' if x>=80 else 'B' if x>=70 else 'C' if x>=60 else 'D'
df['Grade']=df['Marks'].apply(grade)
df.to_csv(OUT/'cleaned_student_data.csv',index=False)
dep=(df.groupby('Department').agg(Students=('Student','count'),Average_Marks=('Marks','mean'),Average_Attendance=('Attendance','mean'),Highest_Marks=('Marks','max')).reset_index())
dep[['Average_Marks','Average_Attendance']]=dep[['Average_Marks','Average_Attendance']].round(2)
dep.to_csv(OUT/'department_summary.csv',index=False)
grade=df['Grade'].value_counts().rename_axis('Grade').reset_index(name='Students'); grade.to_csv(OUT/'grade_summary.csv',index=False)
summary=pd.DataFrame({'Metric':['Original Rows','Original Columns','Duplicates Removed','Missing Marks Filled','Missing Attendance Filled','Final Rows','Final Columns'],'Value':[original_rows,original_cols,dups,missing_marks,missing_att,len(df),len(df.columns)]}); summary.to_csv(OUT/'cleaning_summary.csv',index=False)
for col,title,ylabel,file in [('Average_Marks','Average Marks by Department','Average Marks','average_marks_by_department.png'),('Average_Attendance','Average Attendance by Department','Average Attendance (%)','average_attendance_by_department.png')]:
    plt.figure(figsize=(9,5)); plt.bar(dep['Department'],dep[col]); plt.title(title); plt.xlabel('Department'); plt.ylabel(ylabel); plt.grid(axis='y',alpha=.3); plt.tight_layout(); plt.savefig(OUT/file,dpi=200); plt.close()
plt.figure(figsize=(7,5)); plt.bar(grade['Grade'],grade['Students']); plt.title('Grade Distribution'); plt.xlabel('Grade'); plt.ylabel('Number of Students'); plt.grid(axis='y',alpha=.3); plt.tight_layout(); plt.savefig(OUT/'grade_distribution.png',dpi=200); plt.close()
report=f'''<!doctype html><html><head><meta charset="utf-8"><title>Automated Data Cleaning Report</title><style>body{{font-family:Arial;margin:40px}}table{{border-collapse:collapse;width:90%}}th,td{{border:1px solid #ccc;padding:8px}}th{{background:#eee}}img{{max-width:850px}}</style></head><body><h1>Automated Data Cleaning and Reporting System</h1><p><b>Final students:</b> {len(df)} &nbsp; <b>Average marks:</b> {df.Marks.mean():.2f} &nbsp; <b>Average attendance:</b> {df.Attendance.mean():.2f}%</p><h2>Cleaning Summary</h2>{summary.to_html(index=False)}<h2>Department Summary</h2>{dep.to_html(index=False)}<h2>Grade Distribution</h2>{grade.to_html(index=False)}<h2>Visual Summary</h2><img src="average_marks_by_department.png"><br><img src="average_attendance_by_department.png"><br><img src="grade_distribution.png"><h2>Conclusion</h2><p>The raw dataset was cleaned automatically by handling missing values, removing duplicates, standardizing department names, validating numeric fields, and generating summaries and visualizations.</p></body></html>'''
(OUT/'automated_report.html').write_text(report,encoding='utf-8')
print('Completed:',len(df),'rows; duplicates removed:',dups)
