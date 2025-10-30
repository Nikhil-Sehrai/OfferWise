// Minimal front-end logic for simulator and script studio
(function(){
  function fmt(n){ if(isNaN(n)) return '–'; return '₹ ' + n.toFixed(2) + ' L'; }
  window.offerwiseInit = function(){
    const ctx = window.OFFERWISE_CTX || {};
    const basePct = document.getElementById('basePct');
    const bonusPct= document.getElementById('bonusPct');
    const lvlAsk  = document.getElementById('lvlAsk');
    const basePctV= document.getElementById('basePctV');
    const bonusPctV= document.getElementById('bonusPctV');
    const ctcEl = document.getElementById('ctc');
    const deltaEl = document.getElementById('delta');
    const riskTxt = document.getElementById('riskTxt');
    const riskNote= document.getElementById('riskNote');

    function recalc(){
      const bPct = parseInt(basePct.value||'0');
      const bnPct= parseInt(bonusPct.value||'0');
      basePctV.textContent = bPct+'%'; bonusPctV.textContent = bnPct+'%';
      const newBase  = ctx.base * (1 + bPct/100);
      const newBonus = ctx.bonus * (1 + bnPct/100);
      const levelUp  = (lvlAsk.value==='up');

      let risk = 0; let note=[];
      if(ctx.p50){
        const cap = ctx.base >= ctx.p50 ? 0.15 : 0.25;
        if (bPct/100 > cap) { risk+=2; note.push(`Base ask > ${(cap*100).toFixed(0)}% cap`); }
        if (newBase > ctx.p75*1.05) { risk+=1; note.push('Above P75'); }
        if (levelUp && ctx.base < ctx.p50) { risk+=2; note.push('Level up while below median'); }
      }
      const levers = (bPct!==0) + (bnPct!==0) + (levelUp?1:0) + (ctx.jb>0?1:0);
      if (levers > 2){ risk+=2; note.push('Too many levers (>2)'); }

      const ctc = newBase + newBonus + ctx.jb;
      const delta = ctc - (ctx.base + ctx.bonus + ctx.jb);
      ctcEl.textContent = fmt(ctc);
      deltaEl.textContent = (delta>=0?'+':'') + fmt(delta).replace('₹ ','₹ ');
      const rTxt = risk<=1?'Low':(risk<=3?'Medium':'High');
      riskTxt.textContent = rTxt;
      riskTxt.className = 'badge rounded-pill ' + (risk<=1?'text-bg-success':(risk<=3?'text-bg-warning':'text-bg-danger'));
      riskNote.textContent = note.join(' • ');
    }
    ['input','change'].forEach(ev=>{
      basePct.addEventListener(ev,recalc);
      bonusPct.addEventListener(ev,recalc);
      lvlAsk.addEventListener(ev,recalc);
    });
    recalc();
  };

  window.offerwiseScriptInit = function(){
    const ctx = window.OFFERWISE_CTX || {};
    const tone = document.getElementById('tone');
    const email = document.getElementById('email');
    const gen = document.getElementById('gen');
    const copy = document.getElementById('copy');
    function generate(){
      const base = Number.isFinite(ctx.base) ? ctx.base : 0;
      const target = base * 1.10;                  // simple +10% ask
      const newBase = Number.isFinite(target) ? target.toFixed(1) : '—';

      const lines = [
        `Subject: Offer Discussion — Role: ${ctx.role||'Analyst'}, ${ctx.city||'BLR'}`,
        ``,
        `Hi Recruiter,`,
        `Thank you for the opportunity and the detailed offer. Based on the role scope and ${ctx.city||'Bengaluru'} market data for ${ctx.role||'Analyst'} roles, a base of ₹${newBase}L would reflect the responsibilities well.`,
        `I’m flexible on structure (bonus/joining) to align with team timelines. If we can align on base, I can sign off quickly.`,
        `\nRegards,\nCandidate`
      ];
      email.value = lines.join('\n');
    }
    gen.addEventListener('click', generate);
    copy.addEventListener('click', async ()=>{
      try{ await navigator.clipboard.writeText(email.value); document.getElementById('copied').textContent='Copied.'; setTimeout(()=>document.getElementById('copied').textContent='',1500);}catch(e){}
    });
    generate();
  };
})();