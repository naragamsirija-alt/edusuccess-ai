import streamlit as st, csv, math
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="EduSuccess AI", page_icon="🎓", layout="wide")
st.markdown("""<style>
.title{font-size:42px;font-weight:800}.sub{color:#64748b}
.box{padding:18px;border-radius:14px;margin:8px 0}
.high{background:#fee2e2;border-left:7px solid #dc2626}
.med{background:#fef3c7;border-left:7px solid #d97706}
.low{background:#dcfce7;border-left:7px solid #16a34a}
</style>""", unsafe_allow_html=True)

DATA_FILE = Path(__file__).parent / "students.csv"
FIELDS = ["student_id","name","department","year","attendance","maths",
          "programming","assignments","missed","overall","risk"]

def load_students():
    with open(DATA_FILE, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

students = load_students()

def f(r,k): return float(r[k])
def vec(r):
    return [f(r,"attendance"),f(r,"maths"),f(r,"programming"),
            f(r,"assignments"),f(r,"missed")*12.5]

def label(r):
    s=((100-f(r,"attendance"))*.30+(100-f(r,"maths"))*.25+
       (100-f(r,"programming"))*.15+(100-f(r,"assignments"))*.15+
       f(r,"missed")*4)
    return "High" if s>=38 else "Medium" if s>=22 else "Low"

labels=[r.get("risk") or label(r) for r in students]

def dist(a,b): return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def predict(values,k=5):
    ns=sorted((dist(values,vec(r)),lab)
              for r,lab in zip(students,labels))[:min(k,len(students))]
    votes=Counter(x[1] for x in ns)
    p,n=votes.most_common(1)[0]
    return p,n/len(ns)*100,ns

def rec(a,m,p,ass,miss):
    x=[]
    if a<75: x.append(("Attendance","Schedule mentor follow-up and set an 80%+ weekly target."))
    if m<50: x.append(("Mathematics","Create a 2-week targeted Mathematics practice plan."))
    elif m<65: x.append(("Mathematics","Add weekly Mathematics practice and mentor review."))
    if p<50: x.append(("Programming","Provide coding exercises and peer/mentor support."))
    elif p<65: x.append(("Programming","Recommend extra coding practice on weak topics."))
    if miss>=3: x.append(("Assignments","Prioritise missed assignments and enable reminders."))
    elif miss>=1: x.append(("Assignments","Review outstanding assignments and set weekly targets."))
    if ass<60: x.append(("Coursework","Break coursework into smaller milestones."))
    return x or [("Maintain","Performance is healthy; continue regular monitoring.")]

def next_student_id(rows):
    nums=[]
    for r in rows:
        sid=str(r.get("student_id","")).strip()
        if sid.upper().startswith("STU"):
            try: nums.append(int(sid[3:]))
            except ValueError: pass
    return f"STU{max(nums,default=0)+1:03d}"

def save_new_student(name,department,year,att,maths,prog,ass,miss,risk):
    rows=load_students()
    student_id=next_student_id(rows)
    row={
        "student_id":student_id,"name":name.strip(),"department":department,
        "year":str(year),"attendance":str(att),"maths":str(maths),
        "programming":str(prog),"assignments":str(ass),"missed":str(miss),
        "overall":str(round((att+maths+prog+ass)/4,1)),"risk":risk
    }
    with open(DATA_FILE,"a",encoding="utf-8",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=FIELDS)
        writer.writerow(row)
    return student_id

st.markdown('<div class="title">🎓 EduSuccess AI</div>',unsafe_allow_html=True)
st.markdown('<div class="sub">Student Analytics & Success Platform • Python 3.14 compatible</div>',unsafe_allow_html=True)
st.divider()

page=st.sidebar.radio("Navigation",[
    "🏠 Overview","👨‍🎓 Student Analysis","👩‍🏫 Teacher Analytics",
    "🤝 Mentor Follow-up","🤖 AI Risk Simulator"])

if page=="🏠 Overview":
    ps=[predict(vec(r))[0] for r in students]
    high,med,low=ps.count("High"),ps.count("Medium"),ps.count("Low")
    a,b,c,d=st.columns(4)
    a.metric("Students",len(students)); b.metric("🔴 High Risk",high)
    c.metric("🟠 Medium Risk",med)
    d.metric("Average Score",f"{sum(f(r,'overall') for r in students)/len(students):.1f}%")
    st.subheader("AI Risk Distribution")
    for title,count in [("🔴 High",high),("🟠 Medium",med),("🟢 Low",low)]:
        st.write(f"{title}: **{count}**"); st.progress(count/len(students))
    st.subheader("Students Requiring Attention")
    for r,p in zip(students,ps):
        if p=="High":
            st.write(f"🔴 **{r['name']}** — Attendance {r['attendance']}% | Maths {r['maths']}/100 | Missed {r['missed']}")

elif page=="👨‍🎓 Student Analysis":
    name=st.selectbox("Select student",[r["name"] for r in students])
    r=next(x for x in students if x["name"]==name)
    risk,conf,_=predict(vec(r))
    cls={"High":"high","Medium":"med","Low":"low"}[risk]
    icon={"High":"🔴","Medium":"🟠","Low":"🟢"}[risk]
    st.markdown(f'<div class="box {cls}"><h3>{icon} {risk.upper()} RISK</h3>AI confidence: {conf:.0f}%</div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric("Attendance",r["attendance"]+"%"); b.metric("Maths",r["maths"]+"/100")
    c.metric("Programming",r["programming"]+"/100"); d.metric("Missed",r["missed"])
    st.subheader("Performance")
    for k in ["attendance","maths","programming","assignments"]:
        st.write(f"{k.title()}: {f(r,k):.0f}%"); st.progress(min(f(r,k)/100,1))
    st.subheader("🤖 AI Personalised Improvement Plan")
    for area,action in rec(f(r,"attendance"),f(r,"maths"),f(r,"programming"),f(r,"assignments"),int(r["missed"])):
        st.markdown(f"**{area}:** {action}")
    st.info("ML method: K-Nearest Neighbours (KNN), implemented with Python standard-library code.")

elif page=="👩‍🏫 Teacher Analytics":
    dep=st.selectbox("Department",["All"]+sorted(set(r["department"] for r in students)))
    view=students if dep=="All" else [r for r in students if r["department"]==dep]
    a,b,c=st.columns(3)
    a.metric("Students",len(view))
    b.metric("Avg Attendance",f"{sum(f(r,'attendance') for r in view)/len(view):.1f}%")
    c.metric("Avg Score",f"{sum(f(r,'overall') for r in view)/len(view):.1f}%")
    for k in ["attendance","maths","programming","assignments"]:
        avg=sum(f(r,k) for r in view)/len(view)
        st.write(f"**{k.title()} — {avg:.1f}%**"); st.progress(avg/100)
    st.subheader("Student Monitoring")
    st.dataframe([{
        "Student ID":r.get("student_id",""),"Student":r["name"],
        "Dept":r["department"],"Attendance":r["attendance"],
        "Maths":r["maths"],"Programming":r["programming"],
        "Missed":r["missed"],"Risk":predict(vec(r))[0]
    } for r in view],hide_index=True,use_container_width=True)

elif page=="🤝 Mentor Follow-up":
    name=st.selectbox("Student",[r["name"] for r in students])
    r=next(x for x in students if x["name"]==name)
    risk,conf,_=predict(vec(r))
    st.info(f"Current AI status: **{risk}** | Confidence: **{conf:.0f}%**")
    with st.form("mentor"):
        mentor=st.text_input("Mentor name","Dr. Priya")
        action=st.selectbox("Intervention",["Mentor meeting","Attendance support","Subject tutoring","Assignment support","Academic counselling"])
        notes=st.text_area("Notes","Student agreed to a two-week improvement plan.")
        if st.form_submit_button("Save Follow-up"):
            st.success(f"Follow-up recorded for {name}: {action}")
    st.subheader("Suggested Actions")
    for area,action in rec(f(r,"attendance"),f(r,"maths"),f(r,"programming"),f(r,"assignments"),int(r["missed"]))[:3]:
        st.write(f"• **{area}:** {action}")

else:
    st.subheader("🤖 Live AI Risk Simulator")
    st.write("Enter a new student's details, predict the risk, and save the student automatically to students.csv.")

    name=st.text_input("Student name *",placeholder="e.g. Priya Sharma")
    d1,d2,d3=st.columns(3)
    with d1:
        department=st.selectbox("Department",["CSE","ECE","IT","ME"])
        year=st.selectbox("Year",[1,2,3,4])
        att=st.slider("Attendance (%)",40,100,62)
        maths=st.slider("Mathematics",0,100,38)
    with d2:
        prog=st.slider("Programming",0,100,72)
        ass=st.slider("Assignment score",0,100,55)
        miss=st.slider("Assignments missed",0,8,3)
    with d3:
        st.markdown("### New student")
        st.write("Prediction will be stored in **students.csv**.")
        st.write("A unique Student ID will be generated automatically.")

    if st.button("🚀 Predict Student Risk",type="primary"):
        if not name.strip():
            st.error("Please enter the student name before predicting.")
        else:
            risk,conf,near=predict([att,maths,prog,ass,miss*12.5])
            icon={"High":"🔴","Medium":"🟠","Low":"🟢"}[risk]
            if risk=="Low":
                st.success(f"{icon} {risk.upper()} RISK — {conf:.0f}% AI confidence")
            elif risk=="Medium":
                st.warning(f"{icon} {risk.upper()} RISK — {conf:.0f}% AI confidence")
            else:
                st.error(f"{icon} {risk.upper()} RISK — {conf:.0f}% AI confidence")

            st.subheader("AI Intervention Plan")
            for area,action in rec(att,maths,prog,ass,miss):
                st.markdown(f"**{area}:** {action}")

            st.subheader("Why was the student flagged?")
            reasons=[]
            if att<75: reasons.append(f"Attendance is {att}%.")
            if maths<50: reasons.append(f"Mathematics is {maths}/100.")
            if prog<50: reasons.append(f"Programming is {prog}/100.")
            if miss>=3: reasons.append(f"{miss} assignments are missed.")
            if ass<60: reasons.append(f"Assignment score is {ass}%.")
            for x in reasons or ["No major warning indicators detected."]:
                st.write("• "+x)

            student_id=save_new_student(name,department,year,att,maths,prog,ass,miss,risk)
            st.success(f"✅ Student saved! Student ID: **{student_id}** | Name: **{name.strip()}**")
            st.info("The new student has been appended to students.csv. Open Student Analysis or Overview to see the updated data.")

st.divider()
st.caption("EduSuccess AI • B.Tech Competition Prototype • Python 3.14")
