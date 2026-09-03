import jwt from'jsonwebtoken';import{config}from'./config.js';
export const signToken=u=>jwt.sign({sub:u._id.toString(),tenantId:u.tenantId.toString()},config.jwtSecret,{expiresIn:config.jwtExpiresIn});
export function requireAuth(req,res,next){const token=req.headers.authorization?.replace(/^Bearer\s+/i,'');if(!token)return res.status(401).json({error:'Authentication required'});try{const p=jwt.verify(token,config.jwtSecret);req.auth={userId:p.sub,tenantId:p.tenantId};next()}catch{return res.status(401).json({error:'Invalid or expired token'})}}

