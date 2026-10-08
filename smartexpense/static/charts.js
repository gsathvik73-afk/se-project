(() => {
  const data=JSON.parse(document.getElementById('chart-data').textContent);
  const colors=['#246d51','#54a184','#a4c893','#d6aa54','#758ab6','#a16e99','#d78262','#83928a'];
  function context(id){const canvas=document.getElementById(id),w=canvas.clientWidth,h=220,dpr=window.devicePixelRatio||1;canvas.width=w*dpr;canvas.height=h*dpr;const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);return {ctx,w,h};}
  function draw(){
    let {ctx,w,h}=context('pie'), total=data.categories.reduce((s,c)=>s+Number(c.total),0),angle=-Math.PI/2;
    if(!total){ctx.fillStyle='#dde7df';ctx.beginPath();ctx.arc(w/2,h/2,85,0,2*Math.PI);ctx.fill();ctx.fillStyle='#4c675b';ctx.textAlign='center';ctx.fillText('No expenses',w/2,h/2);}
    data.categories.forEach((c,i)=>{const end=angle+Number(c.total)/total*2*Math.PI;ctx.beginPath();ctx.moveTo(w/2,h/2);ctx.arc(w/2,h/2,85,angle,end);ctx.closePath();ctx.fillStyle=colors[i%colors.length];ctx.fill();angle=end;});
    document.querySelectorAll('.legend li').forEach((li,i)=>li.style.color=colors[i%colors.length]);
    ({ctx,w,h}=context('trend'));const max=Math.max(1,...data.trend.map(t=>Number(t.expense))),left=52,right=w-16,top=18,bottom=h-32;
    ctx.font='11px system-ui';ctx.strokeStyle='#d9e3dc';ctx.fillStyle='#536e60';
    for(let i=0;i<=4;i++){const y=bottom-(bottom-top)*i/4;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();ctx.textAlign='right';ctx.fillText(Math.round(max*i/4).toLocaleString('en-IN'),left-7,y+4);}
    ctx.beginPath();ctx.strokeStyle='#246d51';ctx.lineWidth=3;
    data.trend.forEach((t,i)=>{const x=left+(right-left)*i/5,y=bottom-(bottom-top)*Number(t.expense)/max;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();
    data.trend.forEach((t,i)=>{const x=left+(right-left)*i/5,y=bottom-(bottom-top)*Number(t.expense)/max;ctx.beginPath();ctx.arc(x,y,4,0,2*Math.PI);ctx.fillStyle='#246d51';ctx.fill();ctx.textAlign='center';ctx.fillStyle='#536e60';ctx.fillText(t.month.slice(5),x,h-12);});
  }
  draw();window.addEventListener('resize',draw);
})();
