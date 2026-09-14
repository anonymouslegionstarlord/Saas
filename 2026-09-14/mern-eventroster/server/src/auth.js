import jwt from 'jsonwebtoken';import{config}from'./config.js';
export const tokenFor=user=>jwt.sign({sub:user._id.toString(),tenantId:user.tenantId.toString()},config.jwtSecret,{expiresIn:'8h'});
export function requireAuth(req,res,next){const v=req.headers.authorization||'';if(!v.startsWith('Bearer '))return res.status(401).json({error:'Missing bearer token'});try{req.auth=jwt.verify(v.slice(7),config.jwtSecret);next()}catch{res.status(401).json({error:'Invalid or expired token'})}}

