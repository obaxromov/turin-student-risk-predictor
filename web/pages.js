"use strict";
/* The website's full Teacher / Student / Admin pages. API owns data and permissions. */
Object.assign(L, {
  allStudents:["All students","Все студенты","Barcha talabalar"],
  directoryIntro:["Find a student by ID, group, or support status.","Найдите студента по ID, группе или статусу.","Talabani ID, guruh yoki holat boʻyicha toping."],
  allGroups:["All groups","Все группы","Barcha guruhlar"],
  allStatuses:["All statuses","Все статусы","Barcha holatlar"],
  studentSort:["Sort by","Сортировка","Saralash"],
  highestRisk:["Highest risk first","Сначала высокий риск","Avval xavfi yuqori talabalar"],
  clearStudentFilters:["Clear filters","Сбросить фильтры","Filtrlarni tozalash"],
  shownStudents:["{shown} of {total} students","{shown} из {total} студентов","{total} talabadan {shown} tasi"],
  openStudent:["Open profile: {id}","Открыть профиль: {id}","Profilni ochish: {id}"],
  noUpcoming:["Nothing due soon.","Ближайших заданий нет.","Yaqin topshiriqlar yoʻq."],
  tierOutcome:["Actual failure rate by tier (held-out data)","Доля неуспешных по категориям (тест)","Daraja boʻyicha muvaffaqiyatsizlik (test)"],
  csvQuestions:["Import questions from CSV","Импорт вопросов из CSV","Savollarni CSV dan yuklash"],
  activityWeek:["Weekly engagement · not daily check-ins","Недельная активность · не по дням","Haftalik faollik · kunlik emas"],
  activityPick:["Explore one student's activity","Выберите студента для просмотра","Talaba faolligini tanlang"],
  activityNoHistory:["Only eight weekly summaries are available. Individual daily activity was not recorded.","Доступны только восемь недельных показателей. Дневная история не собиралась.","Faqat sakkiz haftalik koʻrsatkich mavjud. Kunlik tarix yigʻilmagan."],
  studentSearch:["Search student IDs…","Поиск по ID студента…","Talaba ID boʻyicha qidirish…"],
  viewProfile:["Open profile","Открыть профиль","Profilni ochish"],
  back:["Back","Назад","Orqaga"],
  profileTitle:["Student profile","Профиль студента","Talaba profili"],
  revealName:["Reveal name","Показать имя","Ismni koʻrsatish"],
  hideName:["Hide name","Скрыть имя","Ismni yashirish"],
  revealExplain:["Revealing a name is recorded in the audit log.","Просмотр имени фиксируется в журнале.","Ismni koʻrish audit jurnaliga yoziladi."],
  contacted:["Contacted","Связались","Bogʻlanildi"],
  markContact:["Mark contacted","Отметить контакт","Aloqa qilindi"],
  unmarkContact:["Undo contacted","Отменить отметку","Belgini bekor qilish"],
  addNote:["Save note","Сохранить заметку","Izohni saqlash"],
  yourNotes:["Teacher notes","Заметки преподавателя","Oʻqituvchi izohlari"],
  allFeatures:["Academic indicators","Учебные показатели","Taʼlim koʻrsatkichlari"],
  individualTrend:["Eight-week activity","Активность за 8 недель","Sakkiz haftalik faollik"],
  median:["Class median","Медиана класса","Guruh medianasi"],
  percentage:["Percent","Процент","Foiz"],
  why:["Key signals","Основные факторы","Asosiy omillar"],
  noNotes:["No notes yet.","Заметок пока нет.","Hozircha izohlar yoʻq."],
  studentProgress:["My progress","Мой прогресс","Mening natijalarim"],
  ownTarget:["My target","Моя цель","Mening maqsadim"],
  yourProjection:["Your projected pace","Прогноз вашего темпа","Sizning taxminiy surʼatingiz"],
  notForecast:["Simple projection from your recent trend, not a guaranteed result.","Простая проекция по последним неделям — не гарантия результата.","Soʻnggi haftalarga asoslangan oddiy taxmin, kafolat emas."],
  dueSoon:["Upcoming work","Ближайшие задания","Yaqin topshiriqlar"],
  assignmentsLabel:["Assignments","Задания","Topshiriqlar"],
  createAssignment:["New assignment","Новое задание","Yangi topshiriq"],
  assignmentSettings:["Assignment settings","Настройки задания","Topshiriq sozlamalari"],
  assignmentTitle:["Title","Название","Nomi"],
  instructions:["Instructions","Инструкции","Koʻrsatmalar"],
  dueDate:["Deadline (local time)","Срок (местное время)","Muddat (mahalliy vaqt)"],
  course:["Course","Предмет","Fan"],
  category:["Category","Категория","Turkum"],
  mode:["Marking","Проверка","Baholash"],
  written:["Written / upload · teacher graded","Письменная / файл · проверяет преподаватель","Yozma / fayl · oʻqituvchi baholaydi"],
  automatic:["Short questions · auto graded","Короткие вопросы · автопроверка","Qisqa savollar · avtomatik baholash"],
  questions:["Questions","Вопросы","Savollar"],
  question:["Question","Вопрос","Savol"],
  expectedAnswer:["Correct answer","Верный ответ","Toʻgʻri javob"],
  options:["Choices (one per line)","Варианты (каждый с новой строки)","Variantlar (har qatorda bittadan)"],
  addQuestion:["Add question","Добавить вопрос","Savol qoʻshish"],
  points:["Points","Баллы","Ball"],
  tolerance:["Tolerance","Допуск","Xatolik chegarasi"],
  text:["Text","Текст","Matn"],
  number:["Number","Число","Son"],
  choice:["Multiple choice","Выбор ответа","Variant tanlash"],
  attachments:["Attachments (optional)","Вложения (необязательно)","Ilovalar (ixtiyoriy)"],
  submit:["Submit answers","Отправить ответы","Javoblarni yuborish"],
  grade:["Grade","Оценить","Baholash"],
  score:["Score","Баллы","Ball"],
  comment:["Feedback","Комментарий","Izoh"],
  submission:["Submission","Ответ студента","Talaba javobi"],
  submissions:["Student submissions","Ответы студентов","Talabalar javoblari"],
  save:["Save","Сохранить","Saqlash"],
  updateDue:["Update deadline","Изменить срок","Muddatni oʻzgartirish"],
  deleteAssignment:["Delete assignment","Удалить задание","Topshiriqni oʻchirish"],
  deleteConfirm:["Delete this assignment and its submissions?","Удалить задание и все ответы?","Topshiriq va barcha javoblar oʻchirilsinmi?"],
  submitted:["Submitted","Сдано","Topshirildi"],
  notSubmitted:["Not submitted","Не сдано","Topshirilmagan"],
  ungraded:["Awaiting grading","Ожидает оценки","Baho kutilmoqda"],
  closed:["Closed","Закрыто","Yopilgan"],
  open:["Open","Открыто","Ochiq"],
  noAssignments:["No assignments yet.","Заданий пока нет.","Hozircha topshiriqlar yoʻq."],
  emptyCourses:["No assignments for this course yet.","Для этого предмета ещё нет заданий.","Bu fan uchun topshiriqlar yoʻq."],
  allCourses:["Explore courses","Предметы","Fanlarni koʻrish"],
  currentGrade:["My grade","Моя оценка","Mening bahom"],
  modelDisclaimer:["Simulated demonstration data. The model scores are not calibrated probabilities or verified real-world accuracy.","Демонстрационные синтетические данные. Оценки модели не являются проверенными вероятностями или реальной точностью.","Sunʼiy demo maʼlumotlari. Model baholari haqiqiy ehtimollik yoki tasdiqlangan aniqlik emas."],
  tryPredict:["Run prediction","Запустить прогноз","Bashorat qilish"],
  predictOne:["Single student","Один студент","Bitta talaba"],
  predictOneInfo:["Enter attendance, activity, and grades to estimate one student's risk.","Введите посещаемость, активность и оценки, чтобы оценить риск для одного студента.","Bitta talabaning xavfini baholash uchun davomat, faollik va baholarni kiriting."],
  predictBatch:["CSV batch","Пакетный прогноз CSV","CSV orqali guruhni baholash"],
  predictBatchInfo:["Upload several students in one file and download their results.","Загрузите данные нескольких студентов одним файлом и скачайте результаты.","Bir faylda bir nechta talaba maʼlumotlarini yuklang va natijalarni yuklab oling."],
  enterStudentData:["Enter student data","Ввести данные студента","Talaba maʼlumotlarini kiritish"],
  predictFromProfile:["Predict from profile","Прогноз по профилю","Profil asosida bashorat"],
  profilePredictionTitle:["Predict for {id}","Прогноз для {id}","{id} uchun bashorat"],
  profilePredictionIntro:["Review the values from this student’s profile. Any edits apply to this prediction.","Проверьте значения из профиля студента. Изменения учитываются в этом прогнозе.","Talaba profilidagi qiymatlarni tekshiring. Oʻzgarishlar shu bashoratga tatbiq etiladi."],
  profilePredictionBack:["Back to profile","Назад к профилю","Profilga qaytish"],
  resetProfileInputs:["Reset to profile values","Вернуть значения из профиля","Profil qiymatlarini tiklash"],
  followUpNote:["Follow-up note","Заметка о дальнейших действиях","Keyingi qadamlar haqida izoh"],
  saveFollowUpNote:["Save follow-up note","Сохранить заметку","Izohni saqlash"],
  followUpSaved:["Note saved to the student’s profile.","Заметка сохранена в профиле студента.","Izoh talaba profiliga saqlandi."],
  followUpRequired:["Enter a note before saving.","Введите текст заметки.","Saqlashdan oldin izoh kiriting."],
  predictionBack:["Back to Predict","Назад к прогнозам","Bashoratga qaytish"],
  engagementFields:["Attendance and activity","Посещаемость и активность","Davomat va faollik"],
  courseworkFields:["Grades and coursework","Оценки и задания","Baholar va topshiriqlar"],
  useTypicalValues:["Fill with typical values","Заполнить типичными значениями","Odatiy qiymatlar bilan toʻldirish"],
  predictionRange:["Range: {min} to {max}","Диапазон: от {min} до {max}","Oraliq: {min} dan {max} gacha"],
  choosePredictionCsv:["Student CSV file","CSV-файл со студентами","Talabalar uchun CSV fayl"],
  readPredictionCsvError:["Could not read the CSV file.","Не удалось прочитать CSV-файл.","CSV faylni oʻqib boʻlmadi."],
  importCsv:["Score a CSV","Проверить CSV","CSV ni baholash"],
  csvHint:["CSV columns must match all eight model inputs. Maximum 5,000 rows / 2 MB.","CSV должен содержать все восемь параметров. До 5 000 строк / 2 МБ.","CSV sakkizta parametrni oʻz ichiga olishi kerak. 5 000 qator / 2 MB."],
  sampleCsv:["Download sample CSV","Скачать образец CSV","CSV namunasini olish"],
  downloadResults:["Download results","Скачать результаты","Natijalarni yuklash"],
  mlSummary:["Model evaluation","Оценка модели","Model baholash"],
  featureImportance:["Permutation importance","Важность факторов","Omillar ahamiyati"],
  roc:["ROC AUC","ROC AUC","ROC AUC"],
  accuracy:["Accuracy","Точность","Aniqlik"],
  baseline:["Pass-all baseline","Базовая модель","Oddiy bazaviy model"],
  recall:["Recall of flags","Полнота сигналов","Belgilarning toʻliqligi"],
  adminAccounts:["User accounts","Учётные записи","Foydalanuvchi hisoblari"],
  createAccount:["Create account","Создать аккаунт","Hisob yaratish"],
  linkedStudent:["Student ID (if student)","ID студента","Talaba ID si"],
  role:["Role","Роль","Rol"],
  active:["Active","Активен","Faol"],
  inactive:["Inactive","Неактивен","Faol emas"],
  changeRole:["Update role","Изменить роль","Rolni almashtirish"],
  resetPassword:["Reset password","Сбросить пароль","Parolni tiklash"],
  auditLog:["Audit log","Журнал действий","Audit jurnali"],
  accountActions:["Manage account","Управление аккаунтом","Hisobni boshqarish"],
  teacherLabel:["Teacher","Преподаватель","Oʻqituvchi"],
  studentLabel:["Student","Студент","Talaba"],
  adminLabel:["Admin","Администратор","Admin"],
  selectAccount:["Choose an account","Выберите аккаунт","Hisobni tanlang"],
  saveSuccess:["Saved successfully.","Сохранено.","Muvaffaqiyatli saqlandi."],
  noData:["No data available.","Нет данных.","Maʼlumot mavjud emas."],
  filter:["Filter","Фильтр","Filtr"],
  deadlinePast:["Choose a future deadline.","Укажите дату в будущем.","Kelajakdagi muddatni tanlang."],
  tooManyFiles:["Maximum three files per assignment.","Не более трёх файлов на задание.","Har bir topshiriqqa uchtagacha fayl."],
  status:["Status","Статус","Holat"],
  mark:["Mark","Оценка","Baho"],
  viewAssignment:["Open assignment","Открыть задание","Topshiriqni ochish"],
  importedDisclaimer:["Imported data: verify its source and held-out performance. Model scores are not calibrated probabilities.","Импортированные данные: проверьте источник и метрики тестирования. Оценки модели не калиброваны.","Yuklangan maʼlumot: manba va test natijalarini tekshiring. Model ballari kalibrlanmagan."],
  ouladProxyNotes:["OULAD historical records use proxies for attendance and previous results. These are not live Turin students.","Исторические данные OULAD используют заменители посещаемости и прошлых оценок. Это не студенты Турина.","OULAD tarixiy yozuvlarida davomat va oldingi baholar oʻrnida taxminiy koʻrsatkichlar ishlatilgan. Ular Turin talabalarining jonli maʼlumotlari emas."],
  modelSubtitle:["How well the model works on past students","Как модель работает на данных прошлых студентов","Model oldingi talabalar maʼlumotlarida qanchalik yaxshi ishlaydi"],
  rocCaption:["Ranking quality · 0.5 is guessing","Качество ранжирования · 0,5 — случайность","Ajratish sifati · 0,5 — tasodif"],
  accuracyCaption:["Correct on held-out students","Верных ответов на тестовой выборке","Testdagi talabalar uchun toʻgʻri javoblar"],
  baselineCaption:["If everyone is predicted to pass","Если считать, что все сдадут","Hamma oʻtadi deb taxmin qilinsa"],
  recallCaption:["Share of struggling students flagged","Доля выявленных студентов с трудностями","Qiynalayotgan talabalar orasida topilganlar"],
  paceRecent:["Recent four-week activity average","Средняя активность за 4 недели","Soʻnggi 4 haftalik oʻrtacha faollik"],
  paceFalling:["Activity has been falling. Your teacher can help you plan the next steps.","Активность снизилась. Преподаватель поможет составить план.","Faollik pasaydi. Oʻqituvchingiz keyingi qadamlarni rejalashga yordam beradi."],
  paceSteady:["Keep showing up at your own pace.","Продолжайте учиться в удобном темпе.","Oʻzingizga mos surʼatda davom eting."],
  paceRising:["Your recent activity is improving. Keep going!","Ваша активность растёт. Так держать!","Faolligingiz oshmoqda. Davom eting!"],
  paceUnknown:["More weekly activity is needed to describe your pace.","Нужны дополнительные данные об активности.","Faollikni baholash uchun koʻproq haftalik maʼlumot kerak."],
  noNumericForecast:["Recent activity is not a prediction of your future results.","Недавняя активность не предсказывает будущие оценки.","Soʻnggi faollik kelajakdagi baholaringizni bashorat qilmaydi."],
  openCount:["Open","Открыто","Ochiq"],
  downloadQuestionTemplate:["Download question CSV template","Скачать шаблон CSV вопросов","Savollar CSV namunasini yuklash"],
  audit_login_failed:["Unsuccessful login","Неудачный вход","Muvaffaqiyatsiz kirish"],
  audit_login_ok:["Signed in","Вход в систему","Tizimga kirish"],
  audit_logout:["Signed out","Выход из системы","Tizimdan chiqish"],
  audit_create_user:["Created account","Создан аккаунт","Hisob yaratildi"],
  audit_set_role:["Changed role","Изменена роль","Rol oʻzgartirildi"],
  audit_activate:["Activated account","Аккаунт активирован","Hisob faollashtirildi"],
  audit_deactivate:["Deactivated account","Аккаунт отключён","Hisob toʻxtatildi"],
  audit_reset_password:["Reset password","Сброшен пароль","Parol tiklandi"],
  audit_reveal_name:["Revealed student name","Просмотрено имя студента","Talaba ismi koʻrildi"],
  audit_mark_contacted:["Marked contacted","Отмечен контакт","Aloqa belgilandi"],
  audit_unmark_contacted:["Unmarked contacted","Контакт отменён","Aloqa belgisi bekor qilindi"],
  audit_add_note:["Added teacher note","Добавлена заметка","Oʻqituvchi izohi qoʻshildi"],
  audit_create_assignment:["Created assignment","Создано задание","Topshiriq yaratildi"],
  audit_change_deadline:["Changed deadline","Изменён срок","Muddat oʻzgartirildi"],
  audit_delete_assignment:["Deleted assignment","Удалено задание","Topshiriq oʻchirildi"],
  audit_submit_assignment:["Submitted work","Работа отправлена","Ish topshirildi"],
  audit_grade_assignment:["Graded submission","Работа оценена","Ish baholandi"],
  total:["Total","Всего","Jami"],
});

/* Display translations only: English course names remain stable database keys. */
const COURSE_TRANSLATIONS = {
  "Mathematics 1":["Математика 1","Matematika 1"],
  "Mathematics 2":["Математика 2","Matematika 2"],
  "Physics 1":["Физика 1","Fizika 1"],
  "Physics 2":["Физика 2","Fizika 2"],
  "Academic Writing":["Академическое письмо","Akademik yozuv"],
  "Programming 1":["Программирование 1","Dasturlash 1"],
  "Programming 2":["Программирование 2","Dasturlash 2"],
  "Foreign Language 1":["Иностранный язык 1","Chet tili 1"],
  "Foreign Language 2":["Иностранный язык 2","Chet tili 2"],
  "New History of Uzbekistan":["Новейшая история Узбекистана","Oʻzbekistonning eng yangi tarixi"],
  "Philosophy":["Философия","Falsafa"],
  "Religious Studies":["Религиоведение","Dinshunoslik"],
  "Data Structures and Algorithms":["Структуры данных и алгоритмы","Maʼlumotlar tuzilmalari va algoritmlar"]
};
function displayCourse(name) {
  const lang=S.lang;
  const names=COURSE_TRANSLATIONS[String(name||'')];
  return names && lang==='ru'?names[0]:names && lang==='uz'?names[1]:name;
}
function assignmentCount(n) {
  if(S.lang==='ru') {
    const ending=n%10,teens=n%100;
    return n+' '+(ending===1 && teens!==11?'задание':ending>=2&&ending<=4&&(teens<12||teens>14)?'задания':'заданий');
  }
  if(S.lang==='uz')return n+' ta topshiriq';
  return n+' '+(n===1?'assignment':'assignments');
}
function auditAction(code) {return L['audit_'+code]?t('audit_'+code):String(code).replaceAll('_',' ');}

function paneHeading(title, desc, end) {
  return h('div',{class:'page-title'},h('div',null,h('p',{class:'eyebrow'},t('insights')),h('h1',null,title),desc?h('p',{class:'muted'},desc):null),end||null);
}
function notice(msg, ok=false) {return h('p',{class:'ui-notice '+(ok?'success':'') ,role:'status'},msg);}
function requestError(e){
  const detail=e.data?.detail;
  if(detail==='deadline_in_past')return t('deadlinePast');
  if(typeof detail==='string')return (S.i18n[detail]||L[detail])?t(detail):detail;
  return t('neterr');
}
function doRequest(path,opts,then,holder){
  const el=holder||null;
  if(el) el.replaceChildren(h('span',{class:'muted small'},t('loading')));
  api(path,opts).then(d=>{if(then)then(d);}).catch(e=>{if(el)el.replaceChildren(notice(requestError(e)));});
}
function inputField(name,opts={}){return h('label',{class:'control-label'},name,h('input',{class:'field',...opts}));}
function textField(name,opts={}){return h('label',{class:'control-label'},name,h('textarea',{class:'field',rows:'4',...opts}));}
function selectField(name,options,initial,change){
  const s=h('select',{class:'field',onchange:change},options.map(([v,label])=>h('option',{value:String(v),selected:String(v)===String(initial)?true:null},label)));
  return {wrap:h('label',{class:'control-label'},name,s),input:s};
}
function tableHead(cols){return h('thead',null,h('tr',null,cols.map(c=>h('th',{scope:'col'},c))));}
function linkButton(label,cb,kind=''){return h('button',{class:'btn '+kind,type:'button',onclick:cb},label);}
function goTo(path){location.hash='#/'+path;}
function num(v,dec=0){return Number(v).toFixed(dec);}
function formatDue(d){return d ? new Date(d.endsWith('Z')?d.replace(' ','T'):d.replace(' ','T')+'Z').toLocaleString(S.lang==='uz'?'uz-UZ':S.lang==='ru'?'ru-RU':'en-GB',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Tashkent'}):'—';}
function saveBlob(blob,name){const url=URL.createObjectURL(blob),a=h('a',{href:url,download:name});document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),5000);}
async function downloadResource(path,name){
  try{const res=await fetch(path,{headers:{Authorization:'Bearer '+S.token}});if(!res.ok)throw Error('Download unavailable');saveBlob(await res.blob(),name);}
  catch(e){alert(e.message);}
}
function filePayload(file){return new Promise((res,rej)=>{if(file.size>20_000_000){rej(Error('Maximum file size 20 MB'));return;}const r=new FileReader();r.onload=()=>res({name:file.name,data:String(r.result).split(',')[1]});r.onerror=()=>rej(Error('Could not read file'));r.readAsDataURL(file);});}
function featureText(f){const k='feat_'+f;return S.i18n[k]?t(k):f.replace(/_/g,' ');}
function cardText(title,contents,cls=''){return h('section',{class:'card '+cls},h('h2',null,title),...contents);}
function shortReason(reason){return reason ? reasonText(reason):t('dt_why_none');}

function directoryFilters(tier='all'){
  return {tier,query:'',group:'all',sort:tier==='all'?'id':'risk'};
}

/* FULL teacher cohort: no .head() slice, no pagination hiding the rest. */
function studentsPage(d,requestedStatus){
  const totals={all:d.total,help:0,watch:0,ok:0};
  if(Object.hasOwn(totals,requestedStatus)){
    S.studentDirectory=directoryFilters(requestedStatus);
    history.replaceState(history.state,'','#/students');
  }
  const filters=(S.studentDirectory??=directoryFilters());
  d.students.forEach(r=>totals[r.tier]++);
  const list=h('div');
  const search=h('input',{class:'field',type:'search',maxlength:40,autocomplete:'off',placeholder:t('studentSearch'),
    'aria-label':t('studentSearch'),value:filters.query,oninput:draw});
  const groups=[...new Set(d.students.map(r=>r.group))].sort((a,b)=>a.localeCompare(b));
  const gs=selectField(t('filter_group'),[['all',t('allGroups')],...groups.map(g=>[g,g])],filters.group,draw);
  const sort=selectField(t('studentSort'),[['id',t('col_student')],['risk',t('highestRisk')]],filters.sort,draw);
  const count=h('p',{class:'small muted student-count',role:'status'});
  const clear=linkButton(t('clearStudentFilters'),()=>{
    filters.tier='all';
    search.value='';
    gs.input.value='all';
    sort.input.value='id';
    draw();
    search.focus();
  },'quiet');
  const statusButtons=['all','help','watch','ok'].map(k=>h('button',{
    class:'student-filter t-'+k,type:'button','data-tier':k,'aria-pressed':String(k===filters.tier),
    onclick:()=>{filters.tier=k;draw();}
  },h('span',null,t(k==='all'?'allStudents':'tier_'+k)),h('strong',null,totals[k])));
  const columns=['col_student','group','col_tier','col_risk','activity','viewProfile'];
  const cell=(k,child,cls)=>h('td',{class:cls,role:'cell'},h('span',{class:'student-cell-label','aria-hidden':'true'},t(k)),child);
  function draw(){
    Object.assign(filters,{query:search.value,group:gs.input.value,sort:sort.input.value});
    const query=filters.query.trim().toLowerCase();
    const rows=d.students.filter(r=>r.student_id.toLowerCase().includes(query)
      &&(filters.tier==='all'||r.tier===filters.tier)&&(filters.group==='all'||r.group===filters.group))
      .sort((a,b)=>(filters.sort==='risk'?b.risk-a.risk:0)||a.student_id.localeCompare(b.student_id));
    statusButtons.forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.tier===filters.tier)));
    clear.hidden=!filters.query&&filters.tier==='all'&&filters.group==='all'&&filters.sort==='id';
    count.textContent=t('shownStudents',{shown:rows.length,total:d.total});
    const body=rows.map(r=>{
      const fill=h('i');fill.style.width=r.risk+'%';
      return h('tr',{role:'row'},
        cell('col_student',h('strong',null,r.student_id),'id student-identity'),
        cell('group',r.group,'student-group'),
        cell('col_tier',badge(r.tier),'student-status'),
        cell('col_risk',h('div',{class:'risk t-'+r.tier},h('div',{class:'bar','aria-hidden':'true'},fill),h('span',null,r.risk+'%')),'student-risk'),
        cell('activity',num(r.weeks.reduce((a,b)=>a+b,0)/r.weeks.length)+'%','student-activity'),
        h('td',{class:'student-action',role:'cell'},h('a',{class:'btn quiet',href:'#/student/'+encodeURIComponent(r.student_id),
          'aria-label':t('openStudent',{id:r.student_id})},t('viewProfile'),icon('arrow'))));
    });
    list.replaceChildren(rows.length?h('div',{class:'tablewrap all-students'},h('table',{
      class:'tbl student-directory-table',role:'table','aria-label':t('allStudents')},
      tableHead(columns.map(k=>t(k))),h('tbody',{role:'rowgroup'},body))):notice(t('no_matches')));
  }
  const page=h('div',{class:'dashboard inner-page students-workspace'},paneHeading(t('nav_students'),t('directoryIntro'),d.demo?demoPill():null),
    h('section',{class:'card student-directory'},
      h('div',{class:'student-toolbar'},h('div',{class:'student-directory-search'},icon('search'),search),gs.wrap,sort.wrap),
      h('div',{class:'student-filters',role:'group','aria-label':t('allStatuses')},statusButtons),
      h('div',{class:'student-results-header'},count,clear),list));
  draw();return page;
}
function studentDetailPage(d){
  const r=d.student;
  const identity=h('strong',null,r.student_id);
  const reveal=linkButton(t('revealName'),()=>doRequest('/api/students/'+r.student_id+'/reveal',{method:'POST'},name=>{identity.textContent=r.student_id+' · '+(name.name||'—');reveal.textContent=t('hideName');reveal.onclick=()=>{identity.textContent=r.student_id;reveal.textContent=t('revealName');};},null),'quiet');
  const cbtn=linkButton(d.contacted?t('unmarkContact'):t('markContact'),()=>doRequest('/api/students/'+r.student_id+'/contact',{method:'POST'},resp=>{
    cbtn.textContent=resp.contacted?t('unmarkContact'):t('markContact');
    S.overviewCache=null;
  },null));
  const textarea=h('textarea',{class:'field',rows:'3',maxlength:'1000',placeholder:t('note_ph')});
  const notes=h('div',{class:'stack notes-stack'});
  const drawNotes=arr=>notes.replaceChildren(...(arr.length?arr.map(n=>h('div',{class:'note'},h('strong',null,n.author),h('span',{class:'muted small'},n.created_at),h('p',null,n.body))):[h('p',{class:'muted'},t('noNotes'))]));
  drawNotes(d.notes);
  const save=linkButton(t('addNote'),()=>{if(!textarea.value.trim())return;doRequest('/api/students/'+r.student_id+'/notes',{method:'POST',body:{body:textarea.value.trim()}},res=>{drawNotes(res.notes);textarea.value='';},notes);},'primary');
  const b=h('div',{class:'dashboard inner-page'},
    h('div',{class:'sub-nav'},linkButton('← '+t('back'),()=>goTo('students'),'quiet')),
    paneHeading(t('profileTitle'),r.group,d.demo?demoPill():null),
    h('section',{class:'card profile-hero'},h('div',null,h('p',{class:'muted small'},t('col_student')),identity,
      h('div',{class:'profile-status'},badge(r.tier),h('strong',null,r.risk+'%'),h('span',{class:'muted'},t('col_risk')))),
      h('div',{class:'button-row profile-actions'},h('a',{class:'btn primary profile-predict',
        href:'#/predict/student/'+encodeURIComponent(r.student_id)},t('predictFromProfile'),icon('arrow')),
        ...(d.demo?[reveal,cbtn]:[cbtn])),d.demo?h('p',{class:'muted small'},t('revealExplain')):null),
    h('div',{class:'grid feature-grid'},
      cardText(t('allFeatures'),[h('div',{class:'feature-stats'},Object.entries(d.features).map(([f,v])=>h('div',null,h('span',{class:'muted'},featureText(f)),h('b',null,num(v,1)),h('small',null,t('median')+': '+num(d.medians[f],1)))))]),
      cardText(t('individualTrend'),[smallAreaChart(r.weeks,d.class_weeks),h('p',{class:'muted small'},t('activityWeek'))])),
    h('div',{class:'grid feature-grid'},
      cardText(t('why'),[h('div',{class:'stack'},...(d.reasons.length?d.reasons.map((why,i)=>h('p',null,h('b',null,(i+1)+'. '),shortReason(why))):[h('p',{class:'muted'},t('dt_why_none'))]))]),
      cardText(t('yourNotes'),[notes,textarea,save])),
    d.assignments.length?cardText(t('assignmentsLabel'),[profileAssignmentsTable(d.assignments)]):null);
  return b;
}

/* SVG monotone cubic curve. Pixel derivatives are limited so the line won't overshoot. */
function smoothPath(values,W=600,H=220,pad={l:18,r:18,t:18,b:30}){
  if(!values.length)return '';
  const dx=(W-pad.l-pad.r)/Math.max(1,values.length-1);
  const ys=values.map(v=>pad.t+(1-Math.max(0,Math.min(100,v))/100)*(H-pad.t-pad.b));
  if(ys.length===1)return `M${pad.l},${ys[0]}`;
  const diff=ys.slice(1).map((v,i)=>(v-ys[i])/dx);
  const ms=ys.map((v,i)=>i===0?diff[0]:i===ys.length-1?diff[diff.length-1]:
    diff[i-1]*diff[i]<=0?0:2*diff[i-1]*diff[i]/(diff[i-1]+diff[i]));
  let path=`M ${pad.l.toFixed(2)} ${ys[0].toFixed(2)}`;
  for(let i=0;i<ys.length-1;i++){
    const x=pad.l+i*dx;path+=` C ${(x+dx/3).toFixed(2)} ${(ys[i]+ms[i]*dx/3).toFixed(2)} ${(x+dx*2/3).toFixed(2)} ${(ys[i+1]-ms[i+1]*dx/3).toFixed(2)} ${(x+dx).toFixed(2)} ${ys[i+1].toFixed(2)}`;
  }
  return path;
}
function smallAreaChart(values,compare){
  const W=600,H=228,p={l:24,r:18,t:14,b:30},path=smoothPath(values,W,H,p),lastx=W-p.r;
  const lastY=p.t+(1-values[values.length-1]/100)*(H-p.t-p.b);
  const g=svg('svg',{viewBox:`0 0 ${W} ${H}`,class:'chart area-chart',role:'img','aria-label':t('individualTrend')});
  const defs=svg('defs',null,svg('linearGradient',{id:'individual-fill',x1:'0',x2:'0',y1:'0',y2:'1'},
    svg('stop',{offset:'0%','stop-color':'#5188ff','stop-opacity':'.23'}),svg('stop',{offset:'100%','stop-color':'#5188ff','stop-opacity':'0'})));
  g.append(defs);
  [25,50,75,100].forEach(v=>{const y=p.t+(1-v/100)*(H-p.t-p.b);g.append(svg('line',{class:'grid-l',x1:p.l,x2:lastx,y1:y,y2:y}));});
  g.append(svg('path',{d:path+` L ${lastx} ${H-p.b} L ${p.l} ${H-p.b} Z`,fill:'url(#individual-fill)'}));
  if(compare)g.append(svg('path',{d:smoothPath(compare,W,H,p),class:'ln comparison-line'}));
  g.append(svg('path',{d:path,class:'ln blue-line'}),svg('circle',{cx:lastx,cy:lastY,r:4,fill:'#3977f5'}));
  values.forEach((v,i)=>g.append(svg('text',{x:p.l+i*(lastx-p.l)/Math.max(1,values.length-1),y:H-7,'text-anchor':'middle'},i+1)));
  return g;
}
function plainBars(items){const max=Math.max(0.001,...items.map(r=>Math.max(0,r.importance)));
  return h('div',{class:'importance'},items.map(r=>h('div',{class:'importance-row'},h('span',null,featureText(r.feature)),
    h('div',{class:'importance-track'},h('i',{style:null})),h('span',null,(r.importance*100).toFixed(2)))));
}
function modelCaveat(d){return d.source==='oulad'?t('ouladProxyNotes'):(d.demo?t('modelDisclaimer'):t('importedDisclaimer'));}
function modelPage(d){
  const mm=d.metrics;const stats=[['roc',mm.roc_auc],['accuracy',mm.accuracy],['baseline',mm.baseline_accuracy],['recall',mm.recall_flag]];
  const imp=plainBars(d.importance);
  imp.querySelectorAll('.importance-track i').forEach((el,i)=>el.style.width=Math.max(0,d.importance[i].importance/Math.max(.001,...d.importance.map(r=>r.importance))*100)+'%');
  return h('div',{class:'dashboard inner-page'},paneHeading(t('mlSummary'),t('modelSubtitle'),d.demo?demoPill():null),
    h('div',{class:'stat-grid'},stats.map(([key,v])=>statCard(key==='roc'?Number(v).toFixed(2):(v*100).toFixed(1)+'%',t(key),t(key+'Caption'),'activity'))),
    h('div',{class:'grid feature-grid'},cardText(t('featureImportance'),[imp,h('p',{class:'muted small'},modelCaveat(d))]),
      cardText(t('mlSummary'),[
        h('p',null,t('md_data_body',{n:d.n_train,m:d.n_test,r:d.base_rate,f:d.features.map(featureText).join('; ')})),
        h('p',{class:'muted small'},modelCaveat(d))])),
    cardText(t('tierOutcome'),[
      h('div',{class:'tablewrap'},
        h('table',{class:'tbl'},
          tableHead([t('col_tier'),t('total'),t('md_failed')]),
          h('tbody',null,d.tiers.map(r => h('tr',null,
            h('td',null,badge(r.tier)),
            h('td',null,r.students),
            h('td',null,(r.fail_rate*100).toFixed(0)+'%'))))
        )
      )
    ]),
    cardText(t('how_to_read'),[...rich(t('md_how_body'))]));
}
const PREDICTION_FIELDS=[
  ['engagementFields',[
    ['attendance',0,100],['attendance_trend',-100,100],['logins_per_week',0,200],['logins_trend',-100,1000]
  ]],
  ['courseworkFields',[
    ['test_avg',0,100],['hw_completion',0,100],['hw_avg',0,100],['prev_result',0,100]
  ]]
];

function predictPage(d){
  const tools=[
    ['predict/new','predictOne','predictOneInfo','enterStudentData','activity'],
    ['predict/csv','predictBatch','predictBatchInfo','importCsv','people']
  ];
  return h('div',{class:'dashboard inner-page prediction-workspace'},paneHeading(t('pr_title'),t('pr_sub'),d.demo?demoPill():null),
    h('div',{class:'prediction-columns'},tools.map(([route,title,desc,action,symbol])=>
      h('a',{class:'card prediction-option',href:'#/'+route},
        h('span',{class:'stat-icon'},icon(symbol)),h('h2',null,t(title)),h('p',{class:'muted'},t(desc)),
        h('span',{class:'prediction-option-action'},t(action),icon('arrow'))))),
    h('p',{class:'muted small prediction-caveat'},modelCaveat(d)));
}

function predictionPageHeader(d,title,desc,student){
  const back=student?'#/student/'+encodeURIComponent(student.student_id):'#/predict';
  return [
    h('div',{class:'sub-nav'},h('a',{class:'btn quiet prediction-back',href:back},icon('arrow'),
      t(student?'profilePredictionBack':'predictionBack'))),
    paneHeading(t(title,student?{id:student.student_id}:null),t(desc),d.demo?demoPill():null)
  ];
}

function predictionFollowUp(student){
  const note=h('textarea',{class:'field',rows:3,maxlength:1000,required:true,placeholder:t('note_ph'),
    oninput:()=>note.setCustomValidity('')});
  const submit=h('button',{class:'btn',type:'submit'},t('saveFollowUpNote'));
  const message=h('div',{role:'status'});
  return h('form',{class:'prediction-follow-up',onsubmit:async ev=>{
    ev.preventDefault();
    const body=note.value.trim();
    if(submit.disabled)return;
    if(!body){note.setCustomValidity(t('followUpRequired'));note.reportValidity();return;}
    submit.disabled=true;
    message.replaceChildren();
    try{
      await api('/api/students/'+encodeURIComponent(student.student_id)+'/notes',{method:'POST',body:{body}});
      if(note.value.trim()===body)note.value='';
      message.replaceChildren(notice(t('followUpSaved'),true));
    }catch(e){message.replaceChildren(notice(requestError(e)));}
    finally{submit.disabled=false;}
  }},h('label',{class:'control-label'},h('span',null,t('followUpNote')),note),submit,message);
}

function singlePredictionPage(d){
  const student=d.student??null;
  const key=student?.student_id??null;
  const startingValues=student?d.features:d.medians;
  const draft=S.predictionDrafts.get(key)??{
    values:Object.fromEntries(Object.entries(student?startingValues:{}).map(([name,value])=>[name,num(value,1)])),
    result:null
  };
  S.predictionDrafts.set(key,draft);
  let revision=0;
  const result=h('div',{class:'prediction-output',tabindex:'-1','aria-live':'polite'});
  const clearResult=()=>{revision++;draft.result=null;result.replaceChildren();};
  const fields={};
  const sections=PREDICTION_FIELDS.map(([title,items])=>h('section',{class:'card prediction-section'},
    h('h2',null,t(title)),h('div',{class:'form-grid'},items.map(([key,min,max])=>{
      const hint='range-'+key;
      const input=h('input',{class:'field',name:key,type:'number',inputmode:'decimal',min,max,step:'.1',required:true,
        'aria-describedby':hint,value:draft.values[key]??'',
        oninput:()=>{draft.values[key]=input.value;clearResult();}});
      fields[key]=input;
      return h('label',{class:'control-label'},h('span',null,featureText(key)),input,
        h('small',{class:'muted',id:hint},t('predictionRange',{min,max})));
    }))));
  const submit=h('button',{class:'btn primary',type:'submit'},t('tryPredict'));
  const restore=linkButton(t(student?'resetProfileInputs':'useTypicalValues'),()=>{
    Object.entries(fields).forEach(([name,input])=>{
      const value=startingValues?.[name];
      draft.values[name]=input.value=Number.isFinite(value)?num(value,1):'';
    });
    clearResult();
  });
  const showPrediction=prediction=>result.replaceChildren(h('section',{class:'card prediction-result'},
    h('div',{class:'prediction-result-title'},h('h2',null,t('pr_result')),badge(prediction.tier)),
    h('strong',{class:'prediction-score'},prediction.risk+'%'),
    prediction.reasons.length?h('div',null,h('h3',null,t('why')),
      h('ul',null,prediction.reasons.map(reason=>h('li',null,shortReason(reason))))):null,
    h('p',{class:'muted small'},modelCaveat(prediction)),student?predictionFollowUp(student):null));
  if(draft.result)showPrediction(draft.result);
  const form=h('form',{class:'prediction-form',onsubmit:async ev=>{
    ev.preventDefault();
    if(submit.disabled)return;
    submit.disabled=true;
    const submittedRevision=revision;
    draft.result=null;
    result.replaceChildren(h('p',{class:'muted small'},t('loading')));
    try{
      const values=Object.fromEntries(Object.entries(fields).map(([key,input])=>[key,input.valueAsNumber]));
      const prediction=await api('/api/predict',{method:'POST',body:{values}});
      if(submittedRevision===revision&&result.isConnected){
        draft.result=prediction;
        showPrediction(prediction);
        result.focus();
      }
    }catch(e){if(submittedRevision===revision)result.replaceChildren(notice(requestError(e)));}
    finally{submit.disabled=false;}
  }},h('div',{class:'prediction-columns'},sections),h('div',{class:'button-row prediction-actions prediction-form-actions'},submit,restore));
  return h('div',{class:'dashboard inner-page prediction-workspace'},
    predictionPageHeader(d,student?'profilePredictionTitle':'enterStudentData',
      student?'profilePredictionIntro':'predictOneInfo',student),form,result);
}

function csvPredictionPage(d){
  const fileInput=h('input',{type:'file',accept:'.csv,text/csv',class:'field',required:true});
  const result=h('div',{class:'prediction-output','aria-live':'polite'});
  const submit=h('button',{class:'btn primary',type:'submit'},t('importCsv'));
  const downloadSample=linkButton(t('sampleCsv'),()=>{
    const keys=PREDICTION_FIELDS.flatMap(([,fields])=>fields.map(([key])=>key));
    const cells=keys.map(k=>Number.isFinite(d.medians?.[k])?num(d.medians[k],1):'');
    saveBlob(new Blob(['student_id,'+keys.join(',')+'\nS001,'+cells.join(',')+'\n'],{type:'text/csv'}),'template.csv');
  });
  const form=h('form',{class:'stack',onsubmit:async ev=>{
    ev.preventDefault();
    const file=fileInput.files[0];
    if(!file||submit.disabled)return;
    if(file.size>2_000_000){result.replaceChildren(notice(t('csvHint')));return;}
    submit.disabled=true;
    result.replaceChildren(h('p',{class:'muted small'},t('loading')));
    let content;
    try{content=await file.text();}
    catch(e){result.replaceChildren(notice(t('readPredictionCsvError')));submit.disabled=false;return;}
    try{
      const scored=await api('/api/predict/csv',{method:'POST',body:{content}});
      if(scored.problems){result.replaceChildren(notice(JSON.stringify(scored.problems)));return;}
      result.replaceChildren(cardText(t('pr_result'),[
        h('p',{class:'muted small'},scored.rows.length+' '+t('total')),
        h('div',{class:'tablewrap'},h('table',{class:'tbl prediction-csv-table'},
          tableHead([t('col_student'),t('col_risk'),t('col_tier')]),
          h('tbody',null,scored.rows.slice(0,150).map(r=>h('tr',null,h('td',{class:'id'},r.student_id),
            h('td',null,r.risk+'%'),h('td',null,badge(r.tier))))))),
        linkButton(t('downloadResults'),()=>{
          const safe=v=>{const s=String(v);return '"'+(/^[=+\-@]/.test(s)?"'"+s:s).replace(/"/g,'""')+'"';};
          const csv='student_id,risk_percent,status\n'+scored.rows.map(r=>[r.student_id,r.risk,r.tier].map(safe).join(',')).join('\n');
          saveBlob(new Blob([csv],{type:'text/csv'}),'predictions.csv');
        },'primary')
      ],'prediction-csv-results'));
    }catch(e){result.replaceChildren(notice(requestError(e)));}
    finally{submit.disabled=false;}
  }},h('label',{class:'control-label'},t('choosePredictionCsv'),fileInput),
    h('p',{class:'muted small'},t('csvHint')),h('div',{class:'button-row prediction-actions'},submit,downloadSample));
  return h('div',{class:'dashboard inner-page prediction-workspace'},
    predictionPageHeader(d,'predictBatch','predictBatchInfo'),h('section',{class:'card'},form),result);
}
function courseLook(name){
  const n=String(name||'').toLowerCase();
  if(n.includes('math'))return ['math','📐'];
  if(n.includes('physics'))return ['physics','⚛️'];
  if(n.includes('program')||n.includes('algorithm')||n.includes('data structures'))return ['code','💻'];
  if(n.includes('language')||n.includes('writing'))return ['language',n.includes('writing')?'✍️':'🌍'];
  if(n.includes('history'))return ['humanities','🏛️'];
  if(n.includes('philosophy'))return ['humanities','💭'];
  if(n.includes('religious'))return ['humanities','📚'];
  return ['code','📘'];
}
function coursePage(d){
  const detail=h('div');let selected=null;
  const grid=h('div',{class:'course-grid'},d.courses.map(c=>{
    const [courseType,courseEmoji]=courseLook(c.name);
    const el=h('button',{class:'course-tile','data-course-type':courseType,type:'button',onclick:()=>{selected=c.id;grid.querySelectorAll('button').forEach(b=>b.classList.toggle('selected',b===el));
      doRequest('/api/assignments',{},result=>{
        const items=result.assignments.filter(a=>a.course_id===c.id);
        detail.replaceChildren(cardText(displayCourse(c.name),items.length?[assignmentMiniTable(items,S.user.role)]:[h('p',{class:'muted'},t('emptyCourses'))]));
      },detail);
    }},h('span',{class:'course-symbol','aria-hidden':'true'},courseEmoji),h('strong',null,displayCourse(c.name)),h('span',{class:'muted small course-meta'},assignmentCount(c.assignments)+' · '+t('openCount')+': '+c.open));
    return el;
  }));
  return h('div',{class:'dashboard inner-page'},paneHeading(t('allCourses'),t(S.user.role==='student'?'co_sub_student':'co_sub_teacher')),
    grid,detail);
}
function profileAssignmentsTable(items) {
  return h('div',{class:'tablewrap'},h('table',{class:'tbl big-table'},
    tableHead([t('assignmentTitle'),t('course'),t('dueDate'),t('status'),t('mark')]),
    h('tbody',null,items.map(a=>h('tr',null,
      h('td',{class:'id'},a.title),h('td',null,displayCourse(a.course_name||'—')),
      h('td',null,formatDue(a.due_at)),
      h('td',null,a.submitted_at?t('submitted'):(a.closed?t('closed'):t('notSubmitted')),
      h('td',null,a.score===null||a.score===undefined?'—':a.score+' / '+a.max_score)))))));
}
function assignmentMiniTable(items,role){return h('div',{class:'tablewrap'},h('table',{class:'tbl big-table'},
  tableHead([t('assignmentTitle'),t('course'),t('dueDate'),t('status'),t('viewAssignment')]),h('tbody',null,items.map(a=>h('tr',null,
    h('td',{class:'id'},a.title),h('td',null,displayCourse(a.course_name||'—')),h('td',null,formatDue(a.due_at)),
    h('td',null,a.closed?t('closed'):t('open')),
    h('td',null,linkButton(t('open'),()=>goTo('assignment/'+a.id),'quiet')))))));
}
function assignmentsPage(d){
  const courseById=Object.fromEntries(d.courses.map(c=>[c.id,displayCourse(c.name)]));
  const items=d.assignments.map(a=>({...a,course_name:courseById[a.course_id]||'—'}));
  const panel=h('div');let q='';
  const search=h('input',{class:'field',type:'search',placeholder:t('search_student'),oninput:ev=>{q=ev.target.value.toLowerCase();draw();}});
  const draw=()=>panel.replaceChildren(items.filter(a=>a.title.toLowerCase().includes(q)).length?assignmentMiniTable(items.filter(a=>a.title.toLowerCase().includes(q)),S.user.role):notice(t('noAssignments')));
  const newbtn=S.user.role==='teacher'?linkButton('+ '+t('createAssignment'),()=>goTo('new-assignment'),'primary'):null;
  draw();return h('div',{class:'dashboard inner-page'},paneHeading(t('assignmentsLabel'),t('hw_sub_'+S.user.role),newbtn),
    h('section',{class:'card'},h('div',{class:'toolbar'},search,h('span',{class:'muted small'},items.length+' '+t('total'))),panel));
}
function assignmentDetailPage(d){
  const a=d.assignment,teacher=S.user.role==='teacher',sid=S.user.student_id;
  const questions=d.questions||[];
  const action=h('div',{class:'stack'});
  const coreDetail=h('div',{class:'stack'},
    h('div',{class:'meta-chips'},h('span',{class:'pill'},t('hw_cat_'+a.category)),h('span',{class:'pill'},a.closed?t('closed'):t('open')),h('span',{class:'pill'},t('hw_mode_'+a.mode))),
    h('p',null,a.description||'—'),h('p',{class:'muted small'},t('dueDate')+': '+formatDue(a.due_at)),
    ...d.materials.map(m=>linkButton('↓ '+m.filename,()=>downloadResource('/api/materials/'+m.id,m.filename),'quiet')));
  if(teacher){
    const rawdate=h('input',{type:'datetime-local',class:'field',value:a.due_at?new Date(new Date(a.due_at+'Z').getTime()+5*3600000).toISOString().slice(0,16):''});
    const results=h('div',{class:'stack'},...d.submissions.map(s=>{
      const score=h('input',{type:'number',class:'field',min:0,max:a.max_score,step:'.5',value:s.score===null?'':String(s.score)});
      const comment=h('input',{class:'field',value:s.comment||'',maxlength:'1000'});
      const message=h('div');
      return h('div',{class:'submission-row'},h('strong',null,s.student_id),h('span',{class:'muted small'},formatDue(s.submitted_at)),
        h('span',null,s.score===null?t('ungraded'):`${s.score} / ${s.max_score}`),
        s.file_name?linkButton('↓ '+s.file_name,()=>downloadResource('/api/submissions/'+a.id+'/'+s.student_id+'/file',s.file_name),'quiet'):null,
        d.submission_details?.[s.student_id]?.text?h('div',{class:'submitted-text'},h('b',null,t('submission')),h('p',null,d.submission_details[s.student_id].text)):null,
        a.mode==='file'?h('div',{class:'form-grid'},inputField(t('score'),{value:score.value,type:'number',min:'0',max:String(a.max_score),step:'.5',oninput:e=>score.value=e.target.value}),
          inputField(t('comment'),{value:comment.value,oninput:e=>comment.value=e.target.value}),
          linkButton(t('grade'),()=>doRequest('/api/assignments/'+a.id+'/grade',{method:'POST',body:{student_id:s.student_id,score:Number(score.value),comment:comment.value}},()=>message.replaceChildren(notice(t('saveSuccess'),true)),message),'primary'),message):null);
    }));
    action.append(cardText(t('submissions'),[results,questions.length?cardText(t('questions'),questions.map(q=>h('p',null,q.prompt+' — '+q.answer))):null]));
    action.append(cardText(t('assignmentSettings'),[h('label',{class:'control-label'},t('updateDue'),rawdate),
      linkButton(t('updateDue'),()=>doRequest('/api/assignments/'+a.id+'/due',{method:'PUT',body:{due_local:rawdate.value}},()=>goTo('assignment/'+a.id),action),'quiet'),
      linkButton(t('deleteAssignment'),()=>{if(confirm(t('deleteConfirm')))doRequest('/api/assignments/'+a.id,{method:'DELETE'},()=>goTo('assignments'),action);},'danger')]));
  } else {
    if(d.mine){
      action.append(cardText(t('submission'),[notice(d.mine.score===null?t('ungraded'):
        t('score')+': '+d.mine.score+' / '+d.mine.max_score,true),d.mine.comment?h('p',null,d.mine.comment):null]));
    }else if(a.closed){action.append(notice(t('closed')));}else{
      const fields={};
      const entries=a.mode==='key'?questions.map(q=>{
        let field;
        if(q.kind==='choice'){field=h('select',{class:'field'},[h('option',{value:''},'—'),...q.choices.split('|').map(opt=>h('option',{value:opt},opt))]);}
        else field=h('input',{class:'field',type:q.kind==='number'?'number':'text',step:'any',maxlength:'300'});
        fields[q.id]=field;return h('label',{class:'control-label'},q.prompt,field);
      }):[];
      const essay=h('textarea',{class:'field',rows:'6',maxlength:'20000',placeholder:t('submission')});
      const attach=h('input',{class:'field',type:'file'});
      const msg=h('div');
      const form=h('form',{class:'stack',onsubmit:async ev=>{
        ev.preventDefault();let upload=null;
        try{if(attach.files[0]) upload=await filePayload(attach.files[0]);}catch(e){msg.replaceChildren(notice(e.message));return;}
        const body=a.mode==='key'?{answers:Object.fromEntries(Object.entries(fields).map(([k,v])=>[k,v.value]))}:{text:essay.value,file:upload};
        doRequest('/api/assignments/'+a.id+'/submit',{method:'POST',body},()=>goTo('assignments'),msg);
      }},...(a.mode==='key'?entries:[textField(t('submission'),{value:'',oninput:ev=>essay.value=ev.target.value}),h('label',{class:'control-label'},t('attachments'),attach)]),
        h('button',{class:'btn primary',type:'submit'},t('submit')),msg);
      action.append(cardText(t('submit'),[form]));
    }
  }
  return h('div',{class:'dashboard inner-page'},h('div',{class:'sub-nav'},linkButton('← '+t('back'),()=>goTo('assignments'),'quiet')),
    paneHeading(a.title,a.mode==='key'?t('automatic'):t('written')),
    h('div',{class:'grid feature-grid'},cardText(t('instructions'),[coreDetail]),action));
}
function newAssignmentPage(d){
  const fields={};const qList=h('div',{class:'stack'});let questions=[];
  const qKind=selectField(t('mode'),[['text',t('text')],['number',t('number')],['choice',t('choice')]],'text');
  const prompt=h('input',{class:'field'}),answer=h('input',{class:'field'}),choices=h('textarea',{class:'field',rows:'3'}),points=h('input',{class:'field',type:'number',min:0.1,value:'1',step:'.5'}),tolerance=h('input',{class:'field',type:'number',min:0,value:'0',step:'.1'});
  const add=()=>{if(!prompt.value.trim()||!answer.value.trim())return;
    questions.push({kind:qKind.input.value,prompt:prompt.value,answer:answer.value,choices:qKind.input.value==='choice'?choices.value.split('\n').join('|'):'',points:Number(points.value),tolerance:Number(tolerance.value)});
    qList.replaceChildren(...questions.map((q,i)=>h('div',{class:'simple-row'},h('span',null,(i+1)+'. '+q.prompt+' · '+q.kind),linkButton('×',()=>{questions.splice(i,1);addRefresh();},'quiet'))));
    prompt.value='';answer.value='';
  };
  const addRefresh=()=>qList.replaceChildren(...questions.map((q,i)=>h('div',{class:'simple-row'},h('span',null,(i+1)+'. '+q.prompt),linkButton('×',()=>{questions.splice(i,1);addRefresh();},'quiet'))));
  const mode=selectField(t('mode'),[['key',t('automatic')],['file',t('written')]],'key',ev=>{
    questionCard.hidden=ev.target.value==='file';writtenBox.hidden=ev.target.value==='key';
  });
  const co=selectField(t('course'),d.courses.map(c=>[c.id,displayCourse(c.name)]),d.courses[0]?.id);
  const ca=selectField(t('category'),[['homework',t('hw_cat_homework')],['test',t('hw_cat_test')],['exam',t('hw_cat_exam')]],'homework');
  const title=h('input',{class:'field',maxlength:'100',required:true});const desc=h('textarea',{class:'field',rows:'3',maxlength:'2000'});
  const due=h('input',{class:'field',type:'datetime-local',required:true,value:new Date(Date.now()+3*86400000).toISOString().slice(0,16)});
  const max=h('input',{class:'field',type:'number',min:1,max:1000,value:'100'});
  const attachment=h('input',{class:'field',type:'file',multiple:true});
  const writtenBox=h('label',{class:'control-label',hidden:true},t('score'),max);
  const questionCard=cardText(t('questions'),[h('div',{class:'form-grid'},qKind.wrap,inputField(t('question'),{oninput:e=>prompt.value=e.target.value}),
    inputField(t('expectedAnswer'),{oninput:e=>answer.value=e.target.value}),
    textField(t('options'),{oninput:e=>choices.value=e.target.value}),
    inputField(t('points'),{type:'number',value:'1',oninput:e=>points.value=e.target.value}),
    inputField(t('tolerance'),{type:'number',value:'0',oninput:e=>tolerance.value=e.target.value})),
    linkButton(t('addQuestion'),add,'quiet'),qList]);
  const qcsv=h('input',{class:'field',type:'file',accept:'.csv,text/csv'});
  const qcsvStatus=h('div');
  qcsv.addEventListener('change',async()=>{
    const file=qcsv.files?.[0];if(!file)return;
    if(file.size>500_000){qcsvStatus.replaceChildren(notice(t('csvHint')));return;}
    doRequest('/api/questions/parse-csv',{method:'POST',body:{content:await file.text()}},result=>{
      questions.push(...result.questions);addRefresh();qcsvStatus.replaceChildren(notice(result.questions.length+' '+t('questions'),true));
    },qcsvStatus);
  });
  questionCard.append(h('label',{class:'control-label'},t('csvQuestions'),qcsv),
    linkButton(t('downloadQuestionTemplate'),()=>saveBlob(new Blob(['kind,prompt,answer,choices,points,tolerance\nnumber,What is 2 + 2?,4,,1,0\n'],{type:'text/csv'}),'questions-template.csv'),'quiet'),qcsvStatus);
  const msg=h('div');
  const form=h('form',{class:'stack',onsubmit:async ev=>{
    ev.preventDefault();let files=[];try{if(attachment.files.length>3)throw Error(t('tooManyFiles'));files=await Promise.all([...attachment.files].map(filePayload));}catch(e){msg.replaceChildren(notice(e.message));return;}
    const body={title:title.value,description:desc.value,due_local:due.value,mode:mode.input.value,
      category:ca.input.value,course_id:Number(co.input.value),max_score:Number(max.value),questions,materials:files};
    doRequest('/api/assignments',{method:'POST',body},d=>goTo('assignment/'+d.id),msg);
  }},h('div',{class:'form-grid'},h('label',{class:'control-label'},t('assignmentTitle'),title),co.wrap,ca.wrap,mode.wrap,
    h('label',{class:'control-label'},t('dueDate'),due),writtenBox),h('label',{class:'control-label'},t('instructions'),desc),
    h('label',{class:'control-label'},t('attachments'),attachment),questionCard,h('button',{class:'btn primary',type:'submit'},t('createAssignment')),msg);
  return h('div',{class:'dashboard inner-page'},h('div',{class:'sub-nav'},linkButton('← '+t('back'),()=>goTo('assignments'),'quiet')),
    paneHeading(t('createAssignment'),t('hw_sub_teacher')),h('section',{class:'card new-assignment'},form));
}
function homePage(d){
  if(!d.linked)return h('div',{class:'dashboard inner-page'},paneHeading(t('studentProgress')),notice(t('hm_no_link')));
  const featureLabels={attendance:'f_attendance',test_avg:'f_tests',hw_completion:'f_homework'};
  return h('div',{class:'dashboard inner-page'},paneHeading(t('studentProgress'),t('hm_sub'),d.demo?demoPill():null),
    h('div',{class:'stat-grid'},statCard(d.overall+'%',t('hm_overall'),t('hm_overall_cap'),'people'),
      ...Object.entries(d.features).map(([f,v])=>statCard(v+'%',t(featureLabels[f]),t('ownTarget')+': '+d.targets[f]+'%','activity'))),
    h('div',{class:'grid feature-grid'},cardText(t('individualTrend'),[smallAreaChart(d.weeks),
      h('p',{class:'muted small'},t('activityWeek'))]),
      cardText(t('yourProjection'),[
        h('div',{class:'projection-message'},t('pace'+({'falling':'Falling','rising':'Rising','steady':'Steady','unknown':'Unknown'}[d.pace_status]||'Unknown'))),
        h('p',{class:'muted small'},t('paceRecent')+': '+(d.recent_average>0?d.recent_average+'%':t('noData'))),
        h('p',null,t('ownTarget')+': '+d.targets.weekly_activity+'%'),
        h('p',{class:'muted small'},t('noNumericForecast'))])),
    cardText(t('dueSoon'),d.due.length?[assignmentMiniTable(d.due,'student')]:[h('p',{class:'muted'},t('noUpcoming'))]));
}
function accountsPage(d){
  let selected=d.users.find(u=>u.username!==S.user.username)||d.users[0];const list=h('div');const management=h('div',{class:'account-manage'});
  const refresh=()=>doRequest('/api/accounts',{},next=>{d=next;draw();manage();});
  function draw(){list.replaceChildren(h('div',{class:'tablewrap'},h('table',{class:'tbl big-table'},
    tableHead([t('username'),t('role'),t('linkedStudent'),t('active'),t('accountActions')]),
    h('tbody',null,d.users.map(u=>h('tr',null,h('td',{class:'id'},u.username),h('td',null,t('role_'+u.role)),
      h('td',null,u.student_id||'—'),h('td',null,u.active?t('active'):t('inactive')),
      h('td',null,linkButton(t('accountActions'),()=>{selected=u;manage();},'quiet'))))))));}
  function manage(){if(!selected)return;selected=d.users.find(u=>u.id===selected.id)||d.users[0];if(!selected)return;
    const u=selected,role=selectField(t('role'),[['teacher',t('teacherLabel')],['student',t('studentLabel')],['admin',t('adminLabel')]],u.role);
    const id=selectField(t('linkedStudent'),[['','—'],...d.student_ids.map(s=>[s,s])],u.student_id||'');
    const pw=h('input',{class:'field',type:'password',autocomplete:'new-password',minlength:8,placeholder:t('ad_new_pw')});
    const msg=h('div');
    const self=u.username===S.user.username;
    management.replaceChildren(h('h3',null,u.username),
      ...(self?[]:[role.wrap,id.wrap,
        linkButton(t('changeRole'),()=>doRequest('/api/accounts/'+u.id,{method:'PATCH',body:{role:role.input.value,student_id:id.input.value||null}},refresh,msg),'quiet')]),
      h('label',{class:'control-label'},t('resetPassword'),pw),
      linkButton(t('resetPassword'),()=>doRequest('/api/accounts/'+u.id,{method:'PATCH',body:{password:pw.value}},()=>{pw.value='';msg.replaceChildren(notice(t('saveSuccess'),true));},msg),'quiet'),
      ...(self?[]:[linkButton(u.active?t('ad_deactivate'):t('ad_activate'),()=>doRequest('/api/accounts/'+u.id,{method:'PATCH',body:{active:!Boolean(u.active)}},refresh,msg),'danger')]),msg);
  }
  draw();manage();
  const username=h('input',{class:'field',maxlength:'40',required:true});const pass=h('input',{class:'field',type:'password',autocomplete:'new-password',minlength:'8',required:true});
  const role=selectField(t('role'),[['teacher',t('teacherLabel')],['student',t('studentLabel')],['admin',t('adminLabel')]],'teacher');
  const sid=selectField(t('linkedStudent'),[['','—'],...d.student_ids.map(s=>[s,s])],'');const error=h('div');
  const create=h('form',{class:'stack',onsubmit:ev=>{ev.preventDefault();doRequest('/api/accounts',{method:'POST',body:{username:username.value,password:pass.value,role:role.input.value,student_id:sid.input.value||null}},()=>{username.value='';pass.value='';refresh();},error);}},
    h('label',{class:'control-label'},t('username'),username),h('label',{class:'control-label'},t('password'),pass),role.wrap,sid.wrap,
    h('button',{class:'btn primary',type:'submit'},t('createAccount')),error);
  const audit=cardText(t('auditLog'),[h('div',{class:'tablewrap'},h('table',{class:'tbl'},tableHead([t('au_time'),t('au_user'),t('au_action'),t('au_target')]),
    h('tbody',null,d.audit.map(row=>h('tr',null,h('td',null,row.ts),h('td',null,row.username),h('td',null,auditAction(row.action)),h('td',null,row.target||'—'))))))]);
  return h('div',{class:'dashboard inner-page'},paneHeading(t('adminAccounts'),t('ad_sub'),d.demo?demoPill():null),
    cardText(t('adminAccounts'),[list]),h('div',{class:'grid feature-grid'},cardText(t('createAccount'),[create]),cardText(t('accountActions'),[management])),audit);
}
