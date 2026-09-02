import jwt from 'jsonwebtoken';import {config} from './config.js';
export const signToken=user=>jwt.sign({sub:user._id.toString(),tenantId:user.tenantId.toString()},config.jwtSecret,{expiresIn:config.jwtExpiresIn});
export function requireAuth(req,res,next){const token=req.headers.authorization?.replace(/^Bearer\s+/i,'');if(!token)return res.status(401).json({error:'Authentication required'});try{const c=jwt.verify(token,config.jwtSecret);req.auth={userId:c.sub,tenantId:c.tenantId};next()}catch{return res.status(401).json({error:'Invalid or expired token'})}}

