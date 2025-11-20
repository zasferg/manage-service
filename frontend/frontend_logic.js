// ======================
// Helpers
// ======================
const uuidRegex = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/;

function isUUID(v){ return uuidRegex.test((v||"").trim()); }

function showResponse(id, data){
    const el = document.getElementById(id);
    el.textContent = typeof data === 'string' ? data : JSON.stringify(data,null,2);
}

function alertErr(msg){ alert(msg); }

function setToken(t){ localStorage.setItem('api_token', t); updateTokenPreview(); }
function getToken(){ return localStorage.getItem('api_token') || ''; }
function updateTokenPreview(){ /* can be added if token preview needed */ }

// ======================
// API fetch
// ======================
async function apiFetch(method, path, {query=null, body=null, auth=false}={}){
    const base = window.location.origin; // автоматический base URL
    const url = new URL(base + path);
    if(query){ Object.keys(query).forEach(k=> { if(query[k]!==undefined && query[k]!==null) url.searchParams.append(k, query[k]); }); }
    const headers = {'Content-Type':'application/json'};
    if(auth){ const t=getToken(); if(t) headers['Authorization']='Bearer '+t; }
    try{
        const res = await fetch(url.toString(), {method, headers, body: body ? JSON.stringify(body): null});
        let text = await res.text();
        let json;
        try{ json = text ? JSON.parse(text) : {}; } catch(e){ json = { text }; }
        if(!res.ok){ const err = json.detail || json.error || json || text; alertErr('Ошибка: '+res.status+' — '+ (typeof err==='string'?err:JSON.stringify(err))); return {error:err, status:res.status}; }
        return json;
    } catch(e){ alertErr('Network error: '+e.message); return {error:e.message}; }
}

// ======================
// Auth
// ======================
async function registration(){
    const email=document.getElementById('reg_email').value.trim();
    const password=document.getElementById('reg_pass').value;
    if(!email||!password){ alertErr('email и password обязательны'); return; }
    const r = await apiFetch('POST','/auth/registration',{body:{email,password}});
    showResponse('resp_registration', r);
}

async function login(){
    const email=document.getElementById('login_email').value.trim();
    const password=document.getElementById('login_pass').value;
    if(!email||!password){ alertErr('email и password обязательны'); return; }
    const r = await apiFetch('POST','/auth/login',{body:{email,password}});
    showResponse('resp_login', r);
    if(r.access_token) setToken(r.access_token);
}

function logout(){ localStorage.removeItem('api_token'); showResponse('resp_login','logged out'); }

// ======================
// Users
// ======================
async function getMe(){ const r = await apiFetch('GET','/users/me',{auth:true}); showResponse('resp_me',r); }
async function updateMe(){
    const email=document.getElementById('u_email').value || null;
    const password=document.getElementById('u_pass').value || null;
    const company_id=document.getElementById('u_company').value || null;
    if(company_id && !isUUID(company_id)){ alertErr('company_id не UUID'); return; }
    const body={email,password,company_id};
    const r = await apiFetch('PUT','/users/me',{auth:true,body});
    showResponse('resp_update_me',r);
}

// ======================
// Companies
// ======================
async function createCompany(){
    const name=document.getElementById('c_name').value || null;
    const r = await apiFetch('POST','/companies/create',{auth:true,body:{name}});
    showResponse('resp_create_company',r);
}

async function getCompany(){
    const id=document.getElementById('c_get_id').value.trim();
    if(!isUUID(id)){ alertErr('company id должен быть UUID'); return; }
    const r = await apiFetch('GET','/companies/get',{query:{id}});
    showResponse('resp_get_company',r);
}

async function addUserToCompany(){
    const u=document.getElementById('add_user_user_id').value.trim();
    const c=document.getElementById('add_user_company_id').value.trim();
    if(!u||!c){ alertErr('поля не должны быть пустыми'); return; }
    if(!isUUID(u)||!isUUID(c)){ alertErr('UUID неверен'); return; }
    const r = await apiFetch('PUT','/companies/add_user',{auth:true,query:{user_id:u,company_id:c}});
    showResponse('resp_add_user',r);
}

async function deleteUserFromCompany(){
    const u=document.getElementById('del_user_user_id').value.trim();
    const c=document.getElementById('del_user_company_id').value.trim();
    if(!u||!c){ alertErr('поля не должны быть пустыми'); return; }
    if(!isUUID(u)||!isUUID(c)){ alertErr('UUID неверен'); return; }
    const r = await apiFetch('PUT','/companies/delete_user',{auth:true,query:{user_id:u,company_id:c}});
    showResponse('resp_del_user',r);
}

// ======================
// Tasks
// ======================
async function createTask(){
    const desc=document.getElementById('task_desc').value.trim();
    const deadline=document.getElementById('task_deadline').value || null;
    const company_id=document.getElementById('task_company_id').value.trim();
    const perform=document.getElementById('task_perform_user_id').value.trim();
    if(!desc||!company_id||!perform){ alertErr('description, company_id, perform_user_id обязательны'); return; }
    if(!isUUID(company_id)||!isUUID(perform)){ alertErr('UUID неверен'); return; }
    const body={description:desc,deadline,company_id,perform_user_id:perform};
    const r = await apiFetch('POST','/tasks/task',{auth:true,body});
    showResponse('resp_create_task',r);
}

async function getTask(){
    const id=document.getElementById('get_task_id').value.trim();
    if(!isUUID(id)){ alertErr('task_id не UUID'); return; }
    const r = await apiFetch('GET','/tasks/task',{auth:true,query:{task_id:id}});
    showResponse('resp_get_task',r);
}

async function updateStatus(){
    const id=document.getElementById('us_task_id').value.trim();
    const status=document.getElementById('us_new_status').value || null;
    if(!isUUID(id)){ alertErr('task_id не UUID'); return; }
    const r = await apiFetch('PUT','/tasks/update_status',{auth:true,query:{task_id:id,new_status:status}});
    showResponse('resp_update_status',r);
}

async function assignTask(){
    const u=document.getElementById('assign_user_id').value.trim();
    const t=document.getElementById('assign_task_id').value.trim();
    if(!isUUID(u)||!isUUID(t)){ alertErr('UUID неверен'); return; }
    const r = await apiFetch('POST','/tasks/assign_to',{auth:true,query:{user_id:u,task_id:t}});
    showResponse('resp_assign_task',r);
}


// async function createComment(){
//     const task_id=document.getElementById('com_task_id').value.trim();
//     const text=document.getElementById('com_text').value.trim();
//     const to_user=document.getElementById('com_to_user_id').value.trim();
//     if(!task_id||!text||!to_user){ alertErr('поля не должны быть пустыми'); return; }
//     if(!isUUID(task_id)||!isUUID(to_user)){ alertErr('UUID неверен'); return; }
//     const body={task_id:task_id,text:text,to_user_id:to_user};
//     const r = await apiFetch('POST','/tasks/create_comment',{auth:true,body});
//     showResponse('resp_create_comment',r);
// }
async function apiCreateComment() {
    const task_id = document.getElementById('com_task_id').value.trim();
    const text = document.getElementById('com_text').value.trim();
    const to_user = document.getElementById('com_to_user_id').value.trim();

    if(!task_id || !text || !to_user){
        alertErr('поля не должны быть пустыми');
        return;
    }
    if(!isUUID(task_id) || !isUUID(to_user)){
        alertErr('UUID неверен');
        return;
    }

    const body = { task_id, text, to_user_id: to_user,from_user_id: null };
    const r = await apiFetch('POST','/tasks/create_comment',{auth:true, body});

    showResponse('resp_create_comment',r);
}

async function getChatHistory(){
    const t=document.getElementById('chat_task_id').value.trim();
    const u1=document.getElementById('chat_user1').value.trim();
    const u2=document.getElementById('chat_user2').value.trim();
    if(!isUUID(t)||!isUUID(u1)||!isUUID(u2)){ alertErr('UUID неверен'); return; }
    const r = await apiFetch('GET','/tasks/chat_history',{auth:true,query:{task_id:t,user1:u1,user2:u2}});
    showResponse('resp_chat_history',r);
}

// ======================
// Marks
// ======================
async function getMarks(){ const r = await apiFetch('GET','/marks/get_marks',{auth:true}); showResponse('resp_get_marks',r); }
async function getAvgMarks(){
    const from=document.getElementById('avg_from').value.trim();
    const to=document.getElementById('avg_to').value.trim();
    if(!from||!to){ alertErr('from/to обязательны'); return; }
    const r = await apiFetch('GET','/marks/get_avg_marks',{auth:true,query:{from_date:from,to_date:to}});
    showResponse('resp_get_avg',r);
}
async function addRating(){
    const t=document.getElementById('mark_task_id').value.trim();
    const m=document.getElementById('mark_value').value;
    if(!isUUID(t)||!m){ alertErr('task_id и mark обязательны'); return; }
    const mt=Number(m);
    if(mt<1||mt>5){ alertErr('mark 1-5'); return; }
    const r = await apiFetch('POST','/marks/add_rating',{auth:true,body:{task_id:t,mark:mt}});
    showResponse('resp_add_rating',r);
}

// ======================
// Meetings
// ======================
async function getMeetings(){ const r = await apiFetch('GET','/meetings',{auth:true}); showResponse('resp_get_meetings',r); }
async function createMeeting() {
    const uids = document.getElementById('meet_user_ids').value
                  .split(',')
                  .map(s => s.trim())
                  .filter(Boolean);
    const desc = document.getElementById('meet_desc').value.trim();
    const start = document.getElementById('meet_start').value.trim();
    const end = document.getElementById('meet_end').value.trim();

    if (!uids.length || !desc || !start || !end) {
        alert('Все поля обязательны');
        return;
    }

    for (const id of uids) if (!isUUID(id)) { alert('UUID одного из пользователей неверен'); return; }

    const body = {
        user_ids: uids,
        meeting_data: {
            description: desc,
            meeting_starttime: start,
            meeting_endtime: end,
            is_cancelled: false,
            is_finished: false
        }
    };

    const r = await apiFetch('POST', '/meetings', { auth: true, body });
    showResponse('resp_create_meeting', r);
}
async function cancelMeeting(){
    const id=document.getElementById('cancel_meeting_id').value.trim();
    if(!isUUID(id)){ alertErr('meeting_id не UUID'); return; }
    const r = await apiFetch('PUT','/meetings/cancel',{auth:true,query:{meeting_id:id}});
    showResponse('resp_cancel_meeting',r);
}

// ======================
// Calendar
// ======================
async function getCalendarByDay(){
    const y=document.getElementById('cal_year').value.trim();
    const m=document.getElementById('cal_month').value.trim();
    const d=document.getElementById('cal_day').value.trim();
    if(!y||!m||!d){ alertErr('year/month/day обязательны'); return; }
    const r = await apiFetch('GET','/calendar/by_day',{auth:true,query:{year:y,month:m,day:d}});
    showResponse('resp_cal_day',r);
}
async function getCalendarByMonth(){
    const y=document.getElementById('cal_year_m').value.trim();
    const m=document.getElementById('cal_month_m').value.trim();
    if(!y||!m){ alertErr('year/month обязательны'); return; }
    const r = await apiFetch('GET','/calendar/by_month',{auth:true,query:{year:y,month:m}});
    showResponse('resp_cal_month',r);
}
