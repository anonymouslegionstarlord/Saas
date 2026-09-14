import cors from'cors';import express from'express';import{config}from'./config.js';import{router}from'./routes.js';
export const app=express();app.use(cors({origin:config.clientOrigin}));app.use(express.json({limit:'100kb'}));app.get('/api/health',(_q,r)=>r.json({status:'ok'}));app.use('/api',router);app.use((_q,r)=>r.status(404).json({error:'Route not found'}));app.use((e,_q,r,_n)=>{console.error(e);if(e?.name==='CastError')return r.status(404).json({error:'Record not found'});r.status(500).json({error:'Internal server error'})});

