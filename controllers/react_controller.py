"""
react_controller.py  —  Serve React UI tại /ui/*
"""
from flask import Blueprint, session, redirect

react_bp = Blueprint("react", __name__)

REACT_APP_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Hotel Reminder — Quản lý</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',Roboto,sans-serif;background:#f8fafc}
    #root{display:flex;min-height:100vh}
    .sidebar{width:240px;min-height:100vh;background:#0b0e1f;color:#fff;display:flex;flex-direction:column;padding:24px 16px;flex-shrink:0}
    .sidebar-brand{margin-bottom:32px;padding:0 8px}
    .sidebar-brand h2{font-size:1.1rem;font-weight:700}
    .sidebar-brand p{font-size:.78rem;color:#64748b;margin-top:2px}
    .nav-item{display:block;padding:11px 14px;color:#94a3b8;text-decoration:none;border-radius:8px;margin-bottom:4px;cursor:pointer;transition:.18s;font-size:.9rem}
    .nav-item:hover{background:#1e293b;color:#fff}
    .nav-item.active{background:#6366f1;color:#fff;font-weight:600}
    .sidebar-footer{margin-top:auto;padding-top:16px;border-top:1px solid #1e293b}
    .btn-auth{width:100%;padding:10px;border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:.9rem}
    .btn-auth.logout{background:#ef4444;color:#fff}
    .main-content{flex:1;padding:32px;background:#f8fafc;overflow-x:hidden}
    .stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:20px;margin-bottom:28px}
    .stat-card{border-radius:16px;padding:20px;border:1px solid}
    .toolbar{background:#fff;border-radius:14px;padding:14px 18px;display:flex;gap:14px;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,.04);margin-bottom:24px;flex-wrap:wrap}
    .toolbar input{flex:1;padding:9px 14px 9px 40px;border-radius:10px;border:1px solid #e2e8f0;font-size:14px;outline:none;background:#f8fafc;min-width:180px}
    .search-wrap{position:relative;flex:1;display:flex;align-items:center}
    .search-icon{position:absolute;left:12px;color:#94a3b8;pointer-events:none}
    .btn-filter{background:#fff;border:1px solid #e2e8f0;padding:9px 18px;border-radius:10px;font-weight:600;color:#334155;cursor:pointer}
    .room-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
    .room-card{background:#fff;border-radius:16px;padding:20px;border:1px solid #f1f5f9;box-shadow:0 2px 10px rgba(0,0,0,.04)}
    .room-card-head{display:flex;align-items:center;gap:12px;margin-bottom:14px}
    .room-icon{width:44px;height:44px;border-radius:10px;background:#e0e7ff;display:flex;align-items:center;justify-content:center;font-size:22px}
    .room-meta{font-size:13px;color:#64748b;margin-top:2px}
    .room-card-footer{display:flex;justify-content:space-between;align-items:center}
    .badge{padding:4px 12px;border-radius:8px;font-size:13px;font-weight:600}
    .account-table-wrap{background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.05);overflow:hidden;border:1px solid #e2e8f0}
    table{width:100%;border-collapse:collapse}
    th{padding:13px 18px;color:#475569;font-size:.8rem;font-weight:600;text-transform:uppercase;background:#f8fafc;border-bottom:1px solid #e2e8f0;text-align:left}
    td{padding:13px 18px;border-bottom:1px solid #f1f5f9;vertical-align:middle}
    .btn-sm{padding:6px 12px;border-radius:6px;font-size:13px;border:none;cursor:pointer;font-weight:500}
    .btn-lock{background:#ea580c;color:#fff}
    .btn-unlock{background:#0284c7;color:#fff}
    .modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:9999}
    .modal-box{background:#fff;padding:28px;border-radius:14px;width:420px;max-width:95vw;box-shadow:0 20px 40px rgba(0,0,0,.15)}
    .modal-box h3{margin-bottom:18px;font-size:18px}
    .form-col{display:flex;flex-direction:column;gap:12px}
    .form-col input,.form-col select{padding:9px 12px;border-radius:7px;border:1px solid #cbd5e1;font-size:14px}
    .form-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:14px}
    .btn-cancel{background:#94a3b8;color:#fff;padding:8px 16px;border:none;border-radius:7px;cursor:pointer}
    .btn-save{background:#059669;color:#fff;padding:8px 16px;border:none;border-radius:7px;cursor:pointer}
    .btn-add{background:#059669;color:#fff;padding:10px 16px;border:none;border-radius:8px;cursor:pointer;font-weight:500}
    .error-box{background:#fef2f2;color:#dc2626;padding:10px 14px;border-radius:7px;font-size:13px;margin-bottom:10px}
    .page-header{margin-bottom:28px;display:flex;justify-content:space-between;align-items:flex-start}
    .page-header h1{font-size:26px;font-weight:700;color:#1e293b}
    .page-header p{color:#64748b;font-size:14px;margin-top:3px}
    .loading-box{padding:40px;text-align:center;color:#64748b}
    .err-box{padding:20px;background:#fef2f2;color:#dc2626;border-radius:10px}
    select.toolbar-sel{padding:9px 12px;border-radius:7px;border:1px solid #e2e8f0;font-size:14px}
  </style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">
const { useState, useEffect, useCallback, useContext, createContext } = React;

async function apiFetch(path, opts={}) {
  const res = await fetch(path, { headers:{'Content-Type':'application/json',...(opts.headers||{})}, credentials:'same-origin', ...opts });
  const data = await res.json().catch(()=>({}));
  if (!res.ok) throw new Error(data.message||'Có lỗi xảy ra');
  return data;
}

const AuthCtx = createContext(null);
function AuthProvider({children}) {
  const [user,setUser]=useState(null);
  const [checking,setChecking]=useState(true);
  useEffect(()=>{ apiFetch('/api/auth/me').then(d=>setUser(d.data)).catch(()=>setUser(null)).finally(()=>setChecking(false)); },[]);
  const logout=useCallback(async()=>{ await apiFetch('/api/auth/logout',{method:'POST'}).catch(()=>{}); window.location.href='/login'; },[]);
  return <AuthCtx.Provider value={{user,logout,checking}}>{children}</AuthCtx.Provider>;
}
function useAuth(){return useContext(AuthCtx);}

function Sidebar({page,setPage}) {
  const {user,logout}=useAuth();
  const nav=(id,label)=>(
    <span key={id} className={`nav-item${page===id?' active':''}`} onClick={()=>setPage(id)}>{label}</span>
  );
  return (
    <aside className="sidebar">
      <div className="sidebar-brand"><h2>Hotel Admin</h2><p>Notification System</p></div>
      <nav>
        <a className="nav-item" href="/reminders/dashboard">🏠 Dashboard</a>
        {nav('rooms','🛏️ Phòng (Rooms)')}
        {nav('accounts','👥 Tài khoản')}
        <a className="nav-item" href="/reminders">🔔 Lịch nhắc</a>
        <a className="nav-item" href="/guests">👤 Khách hàng</a>
        <a className="nav-item" href="/bookings">📅 Đặt phòng</a>
        <a className="nav-item" href="/housekeeping">🧹 Dọn phòng</a>
        <a className="nav-item" href="/notifications/internal">📢 Thông báo</a>
        <a className="nav-item" href="/report">📊 Báo cáo</a>
      </nav>
      <div className="sidebar-footer">
        {user&&<div style={{marginBottom:10,fontSize:13,color:'#94a3b8'}}>
          👤 {user.username} <span style={{background:'#1e293b',padding:'2px 6px',borderRadius:4,marginLeft:4}}>{user.role}</span>
        </div>}
        <button className="btn-auth logout" onClick={logout}>Đăng xuất</button>
      </div>
    </aside>
  );
}

function RoomPage() {
  const [rooms,setRooms]=useState([]);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState(null);
  const [search,setSearch]=useState('');
  const fetchRooms=useCallback(()=>{
    setLoading(true);
    apiFetch('/api/rooms').then(d=>{setRooms(d.data||[]);setError(null);}).catch(e=>setError(e.message)).finally(()=>setLoading(false));
  },[]);
  useEffect(()=>{fetchRooms();},[fetchRooms]);
  const total=rooms.length, occupied=rooms.filter(r=>r.status==='occupied').length,
    vacant=rooms.filter(r=>r.status==='available').length, maint=rooms.filter(r=>r.status==='maintenance').length;
  const filtered=rooms.filter(r=>r.room_number?.toString().includes(search)||r.room_type?.toLowerCase().includes(search.toLowerCase()));
  function getBadge(s){
    if(s==='available') return{bg:'#e0f2fe',color:'#0369a1',text:'Trống'};
    if(s==='occupied')  return{bg:'#e0e7ff',color:'#4f46e5',text:'Đang ở'};
    if(s==='maintenance')return{bg:'#fff7ed',color:'#c2410c',text:'Bảo trì'};
    return{bg:'#f1f5f9',color:'#475569',text:s};
  }
  if(loading) return <div className="loading-box">🔄 Đang tải danh sách phòng...</div>;
  if(error)   return <div className="err-box">⚠️ {error}</div>;
  return (
    <div>
      <div className="page-header">
        <div><h1>Room Management</h1><p>Monitor and manage all hotel rooms</p></div>
        <a href="/rooms/create" style={{background:'#2563eb',color:'#fff',padding:'10px 18px',borderRadius:8,textDecoration:'none',fontWeight:600,fontSize:14}}>+ Thêm phòng</a>
      </div>
      <div className="stat-grid">
        {[{label:'Total Rooms',value:total,bg:'#eff6ff',border:'#dbeafe'},{label:'Occupied',value:occupied,bg:'#eef2ff',border:'#e0e7ff'},{label:'Vacant',value:vacant,bg:'#f8fafc',border:'#e2e8f0'},{label:'Maintenance',value:maint,bg:'#fff7ed',border:'#ffedd5'}].map(s=>(
          <div key={s.label} className="stat-card" style={{backgroundColor:s.bg,borderColor:s.border}}>
            <p style={{color:'#475569',fontSize:14,fontWeight:500}}>{s.label}</p>
            <h2 style={{fontSize:32,fontWeight:700,color:'#1e293b',marginTop:8}}>{s.value}</h2>
          </div>
        ))}
      </div>
      <div className="toolbar">
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input placeholder="Tìm theo số phòng hoặc loại phòng..." value={search} onChange={e=>setSearch(e.target.value)}/>
        </div>
        <button className="btn-filter">🎛️ Lọc</button>
      </div>
      {filtered.length===0 ? (
        <div style={{textAlign:'center',padding:40,color:'#94a3b8',background:'#fff',borderRadius:12}}>Không có phòng nào khớp.</div>
      ) : (
        <div className="room-grid">
          {filtered.map(room=>{
            const b=getBadge(room.status);
            return (
              <div key={room.id} className="room-card">
                <div className="room-card-head">
                  <div className="room-icon">🛏️</div>
                  <div>
                    <div style={{fontWeight:700,fontSize:20,color:'#1e293b'}}>{room.room_number}</div>
                    <div className="room-meta">Tầng {room.floor} • {room.room_type}</div>
                  </div>
                </div>
                <div className="room-card-footer">
                  <span className="badge" style={{background:b.bg,color:b.color}}>{b.text}</span>
                  <a href={`/rooms/${room.id}/edit`} style={{background:'#e2e8f0',color:'#475569',padding:'5px 10px',borderRadius:6,textDecoration:'none',fontSize:13}}>✏️ Sửa</a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function AccountPage() {
  const [accounts,setAccounts]=useState([]);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState(null);
  const [keyword,setKeyword]=useState('');
  const [roleFilter,setRoleFilter]=useState('');
  const [statusFilter,setStatusFilter]=useState('');
  const [modalOpen,setModalOpen]=useState(false);
  const [form,setForm]=useState({name:'',email:'',password:'',role:'staff',department:'reception',phone:''});
  const [formErr,setFormErr]=useState('');
  const fetchAccounts=useCallback(()=>{
    setLoading(true);
    const p=new URLSearchParams();
    if(keyword) p.set('keyword',keyword);
    if(roleFilter) p.set('role',roleFilter);
    if(statusFilter) p.set('status_filter',statusFilter);
    apiFetch(`/api/users?${p}`).then(d=>{setAccounts(d.data||[]);setError(null);}).catch(e=>setError(e.message)).finally(()=>setLoading(false));
  },[keyword,roleFilter,statusFilter]);
  useEffect(()=>{fetchAccounts();},[fetchAccounts]);
  async function toggleStatus(id){
    try{ const r=await apiFetch(`/api/users/${id}/toggle-status`,{method:'PATCH'}); setAccounts(prev=>prev.map(a=>a.id===id?{...a,status:r.data.status}:a)); }
    catch(e){ alert('⚠️ '+e.message); }
  }
  async function createUser(e){
    e.preventDefault(); setFormErr('');
    try{ await apiFetch('/api/users',{method:'POST',body:JSON.stringify(form)}); setModalOpen(false); setForm({name:'',email:'',password:'',role:'staff',department:'reception',phone:''}); fetchAccounts(); }
    catch(e){ setFormErr(e.message); }
  }
  function roleBadge(r){
    if(r==='admin')        return{bg:'#fee2e2',color:'#991b1b',text:'Quản trị viên'};
    if(r==='manager')      return{bg:'#fef3c7',color:'#92400e',text:'Quản lý'};
    if(r==='receptionist') return{bg:'#e0f2fe',color:'#0369a1',text:'Lễ tân'};
    if(r==='housekeeping') return{bg:'#f3e8ff',color:'#6b21a8',text:'Buồng phòng'};
    return{bg:'#f1f5f9',color:'#475569',text:r};
  }
  return (
    <div>
      <div className="page-header">
        <div><h1>Quản lý tài khoản nhân viên</h1><p>Danh sách tài khoản phân theo phòng ban</p></div>
        <button className="btn-add" onClick={()=>setModalOpen(true)}>+ Cấp tài khoản mới</button>
      </div>
      <div className="toolbar">
        <div className="search-wrap"><span className="search-icon">🔍</span>
          <input placeholder="Tìm theo tên, email..." value={keyword} onChange={e=>setKeyword(e.target.value)} onKeyDown={e=>e.key==='Enter'&&fetchAccounts()}/>
        </div>
        <select className="toolbar-sel" value={roleFilter} onChange={e=>setRoleFilter(e.target.value)}>
          <option value="">-- Tất cả chức vụ --</option>
          <option value="admin">Quản trị viên</option><option value="manager">Quản lý</option>
          <option value="receptionist">Lễ tân</option><option value="housekeeping">Buồng phòng</option><option value="staff">Nhân viên</option>
        </select>
        <select className="toolbar-sel" value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}>
          <option value="">-- Tất cả trạng thái --</option>
          <option value="active">Hoạt động</option><option value="locked">Tạm khóa</option>
        </select>
      </div>
      {loading?<div className="loading-box">🔄 Đang tải...</div>:error?<div className="err-box">⚠️ {error}</div>:(
        <div className="account-table-wrap">
          <table>
            <thead><tr><th>Họ tên</th><th>Email</th><th>Bộ phận</th><th>Chức vụ</th><th>Trạng thái</th><th style={{textAlign:'center'}}>Hành động</th></tr></thead>
            <tbody>
              {accounts.length===0?<tr><td colSpan="6" style={{padding:32,textAlign:'center',color:'#9ca3af'}}>Không tìm thấy nhân viên nào.</td></tr>
              :accounts.map(acc=>{const rb=roleBadge(acc.role);return(
                <tr key={acc.id}>
                  <td style={{fontWeight:500}}>{acc.name}</td>
                  <td style={{color:'#475569'}}>{acc.email}</td>
                  <td style={{color:'#64748b',textTransform:'capitalize'}}>{acc.department}</td>
                  <td><span className="badge" style={{background:rb.bg,color:rb.color}}>{rb.text}</span></td>
                  <td><span style={{color:acc.status==='active'?'#16a34a':'#dc2626',fontWeight:600}}>{acc.status==='active'?'● Hoạt động':'● Tạm khóa'}</span></td>
                  <td style={{textAlign:'center'}}>
                    <button className={`btn-sm ${acc.status==='active'?'btn-lock':'btn-unlock'}`} onClick={()=>toggleStatus(acc.id)}>
                      {acc.status==='active'?'Khóa lại':'Mở khóa'}
                    </button>
                  </td>
                </tr>
              );})}
            </tbody>
          </table>
        </div>
      )}
      {modalOpen&&(
        <div className="modal-backdrop" onClick={e=>e.target===e.currentTarget&&setModalOpen(false)}>
          <div className="modal-box">
            <h3>Cấp Tài Khoản Nhân Viên Mới</h3>
            {formErr&&<div className="error-box">⚠️ {formErr}</div>}
            <form onSubmit={createUser} className="form-col">
              <input type="text" placeholder="Họ và tên *" required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/>
              <input type="email" placeholder="Email *" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/>
              <input type="password" placeholder="Mật khẩu *" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/>
              <input type="text" placeholder="Số điện thoại" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})}/>
              <label style={{fontSize:13,color:'#475569'}}>Chức vụ:</label>
              <select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}>
                <option value="admin">Quản trị viên</option><option value="manager">Quản lý</option>
                <option value="receptionist">Lễ tân</option><option value="housekeeping">Buồng phòng</option><option value="staff">Nhân viên</option>
              </select>
              <div className="form-actions">
                <button type="button" className="btn-cancel" onClick={()=>setModalOpen(false)}>Hủy</button>
                <button type="submit" className="btn-save">Lưu lại</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const {user,checking}=useAuth();
  const getPage=()=>{const h=window.location.hash.replace('#','');return['rooms','accounts'].includes(h)?h:'rooms';};
  const [page,setPage]=useState(getPage);
  useEffect(()=>{window.location.hash=page;},[page]);
  if(checking) return <div style={{padding:60,textAlign:'center',fontSize:16,color:'#64748b'}}>⏳ Đang tải...</div>;
  if(!user){window.location.href='/login';return null;}
  return (
    <React.Fragment>
      <Sidebar page={page} setPage={setPage}/>
      <main className="main-content">
        {page==='rooms'    && <RoomPage/>}
        {page==='accounts' && <AccountPage/>}
      </main>
    </React.Fragment>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<AuthProvider><App/></AuthProvider>);
</script>
</body>
</html>"""


@react_bp.route("/ui/")
@react_bp.route("/ui")
@react_bp.route("/ui/<path:path>")
def react_app(path=""):
    if "user_id" not in session:
        return redirect("/login")
    return REACT_APP_HTML
