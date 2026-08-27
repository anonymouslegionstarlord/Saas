export const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value||'');
export const validDate=value=>/^\d{4}-\d{2}-\d{2}$/.test(value||'')&&!Number.isNaN(Date.parse(value+'T00:00:00Z'));
export const validTime=value=>/^([01]\d|2[0-3]):[0-5]\d$/.test(value||'');
export function validateShift(data){const errors=[];if(!String(data.employeeName||'').trim())errors.push('employeeName');if(!validEmail(data.employeeEmail))errors.push('employeeEmail');if(!validDate(data.date))errors.push('date');if(!validTime(data.start)||!validTime(data.end)||data.end<=data.start)errors.push('time');if(!String(data.role||'').trim())errors.push('role');return errors}
