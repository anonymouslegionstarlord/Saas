export const validEmail=value=>/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value||'');
export const validDate=value=>/^\d{4}-\d{2}-\d{2}$/.test(value||'')&&!Number.isNaN(Date.parse(value+'T00:00:00Z'));
export function validateDesk(data){const errors=[];if(!/^[A-Za-z0-9_-]{2,20}$/.test(String(data.code||'')))errors.push('code');if(String(data.location||'').trim().length<2)errors.push('location');if(!String(data.floor||'').trim())errors.push('floor');return errors}
export function validateBooking(data){const errors=[];if(!String(data.deskId||'').trim())errors.push('deskId');if(!validDate(data.date))errors.push('date');if(String(data.employeeName||'').trim().length<2)errors.push('employeeName');if(!validEmail(data.employeeEmail))errors.push('employeeEmail');return errors}
