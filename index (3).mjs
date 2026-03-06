//۩❦۩¤═══¤𝑺𝑨𝑺𝑼𝑲𝑬 𝑩𝑶𝑻¤═══¤۩❦۩
//✦•┈๑⋅⋯ ⋯⋅๑┈•✦𝐒𝐄𝐗 𝐖𝐈𝐓𝐇 𝐖𝐏 𝐆𝐀𝐖𝐃𝐒 𝐌𝐎𝐌✦•┈๑⋅⋯ ⋯⋅๑┈•✦
//۩❦۩¤═══¤ 𝐖𝐀𝐍𝐍𝐀 𝐒𝐔𝐂𝐊 𝐌𝐘 𝐃𝐈𝐇𝐇 ¤═══¤۩❦۩

const ALIVE_MSG = `۩❦۩¤═══¤𝑺𝑨𝑺𝑼𝑲𝑬 𝑩𝑶𝑻¤═══¤۩❦۩


✦•┈๑⋅⋯ ⋯⋅๑┈•✦𝐒𝐄𝐗 𝐖𝐈𝐓𝐇 𝐖𝐏 𝐆𝐀𝐖𝐃𝐒 𝐌𝐎𝐌✦•┈๑⋅⋯ ⋯⋅๑┈•✦


۩❦۩¤═══¤ 𝐖𝐀𝐍𝐍𝐀 𝐒𝐔𝐂𝐊 𝐌𝐘 𝐃𝐈𝐇𝐇 ¤═══¤۩❦۩`;

import makeWASocket, {
    useMultiFileAuthState,
    DisconnectReason,
    delay,
    fetchLatestBaileysVersion,
    Browsers,
    downloadMediaMessage
} from '@whiskeysockets/baileys';
import { Boom }          from '@hapi/boom';
import pino              from 'pino';
import fs                from 'fs';
import readline          from 'readline';
import gtts              from 'node-gtts';
import { spawnSync }     from 'child_process';
import ffmpegPath        from 'ffmpeg-static';

// ─────────────────────────────────────────────
//  STORAGE PATHS
// ─────────────────────────────────────────────
const PATH_AUTH    = (id) => `./sessions/${id}`;
const PATH_USERS   = './store/users.json';
const PATH_NETWORK = './store/network.json';
const PATH_TIMING  = './store/timing.json';

// ─────────────────────────────────────────────
//  EMOJI BANKS  (name-change sets)
// ─────────────────────────────────────────────
const SETS = {
    faces:   ['🤡','🥸','😶‍🌫️','🫠','🥴','🤑','😈','👿','😵‍💫','🤧','🥲','😬','🫡','🧑‍💻','🧐'],
    hearts:  ['🎋','🎍','🪴','🎑','🌾','🍀','🌴','🪦','🌵','🎄','🍄','🍃','🌿','🍁','🌴'],
    hands:   ['🍕','🍔','🌮','🍜','🍣','🍩','🧁','🍰','🧋','🥞','🫔','🥙','🧆','🥗','🫕'],
    flowers: ['🏗️','🏚️','🏠','🏡','🏢','🏣','🏤','🏥','🏦','🏧','🏨','🏩','🏪','🏫','🏬'],
    sky:     ['⚽','🏀','🏈','⚾','🎾','🏐','🏉','🥏','🎱','🏑','🏒','🥍','🏸','🥊','🪃'],
    animals: ['🎸','🎹','🎺','🎻','🥁','🪕','🎷','🪗','🎙️','🎚️','🎛️','📻','🪘','🪈','🎼'],
    fruits:  ['🚂','🛳️','🏎️','🚁','🛻','🚡','🛶','🚤','🚠','🛺','🚜','🏍️','🛵','🚲','🛴'],
};

const FLAG_CYCLE = [
    '🇳🇵','🇧🇩','🇱🇰','🇲🇾','🇹🇭','🇻🇳','🇵🇭','🇮🇩','🇸🇬','🇰🇿',
    '🇺🇿','🇦🇿','🇬🇪','🇮🇶','🇮🇷','🇸🇾','🇯🇴','🇱🇧','🇾🇪','🇲🇳'
];

const EMO_CYCLE = [
    '🪬','🧿','🪩','🪸','🪼','🫎','🪿','🦤','🪭','🪮',
    '🪈','🪗','🪘','🪃','🪁','🫙','🪣','🫗','🪤','🪆'
];

const WORD_CYCLE = [
    'CHUD🪣','TMKL🫏','TMKC🪲','CHUDAI KHA🪳','CHUDJA🦠',
    'MAR JA🚽','MAR MAT🗑️','TMKC MAY SALT🧂','TERI MAA PANEER KHA KAR CHODUNGA🪤',
    'RNDI🧻','BITCH🦟','TERI MAA KA BLACKHOLE🕳️','BITCH SON🪰','DICKLESS🤡','TATTI💩'
];

// ─────────────────────────────────────────────
//  FONT CONVERTER  (small caps)
// ─────────────────────────────────────────────
const GLYPH = {
    a:'ᴀ',b:'ʙ',c:'ᴄ',d:'ᴅ',e:'ᴇ',f:'ғ',g:'ɢ',h:'ʜ',i:'ɪ',j:'ᴊ',k:'ᴋ',l:'ʟ',
    m:'ᴍ',n:'ɴ',o:'ᴏ',p:'ᴘ',q:'ǫ',r:'ʀ',s:'ꜱ',t:'ᴛ',u:'ᴜ',v:'ᴠ',w:'ᴡ',x:'x',y:'ʏ',z:'ᴢ',
    A:'ᴀ',B:'ʙ',C:'ᴄ',D:'ᴅ',E:'ᴇ',F:'ғ',G:'ɢ',H:'ʜ',I:'ɪ',J:'ᴊ',K:'ᴋ',L:'ʟ',
    M:'ᴍ',N:'ɴ',O:'ᴏ',P:'ᴘ',Q:'ǫ',R:'ʀ',S:'ꜱ',T:'ᴛ',U:'ᴜ',V:'ᴠ',W:'ᴡ',X:'x',Y:'ʏ',Z:'ᴢ'
};
const g = str => str.split('').map(c => GLYPH[c] ?? c).join('');

// ─────────────────────────────────────────────
//  MENU  (matches your requested format exactly)
// ─────────────────────────────────────────────
const MENU_TEXT = () => `◈  ${g('sasuke bot')} v1
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔐  ${g('ACCESS CONTROL')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .admin      ${g('claim admin in dm')}
  .unadmin    ${g('drop your admin')}
  .sub        ${g('promote someone (reply)')}
  .unsub      ${g('demote someone (reply)')}
  .addbot     ${g('link a new number')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚔️  ${g('NAME CHANGE ARSENAL')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .f1  [${g('text')}]   🤡🥸🤑  ${g('cursed faces')}
  .f2  [${g('text')}]   🎋🪴🌵  ${g('plants')}
  .f3  [${g('text')}]   🍕🍔🧋  ${g('food & drink')}
  .f4  [${g('text')}]   🏗️🏠🏢  ${g('buildings')}
  .f5  [${g('text')}]   ⚽🏀🥊  ${g('sports')}
  .f6  [${g('text')}]   🎸🎹🥁  ${g('music')}
  .f7  [${g('text')}]   🚂🛳️🏎️  ${g('vehicles')}

  .fstop       ${g('stop all name changes')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌀  ${g('CYCLE MODES')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .nc      [${g('text')}]   ${g('word cycle (13 words)')}
  .stopnc

  .conemo  [${g('text')}]   ${g('20 flag cycle')} 🏳️
  .stopconemo

  .ncemo   [${g('text')}]   ${g('20 emoji cycle')} 🎭
  .stopncemo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💬  ${g('MESSAGE ATTACKS')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .spam    [${g('text')}]   ${g('flood the chat')}
  .stopspam

  .swipe   [${g('reply')}]  ${g('auto-reply everyone')}
  .stopswipe

  .txt     [${g('text')}] [${g('ms')}]   ${g('timed text loop')}
  .stoptxt

  .slide   [${g('text')}] [${g('ms')}]   ${g('reply-slide spam')}
  .stopslide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎤  ${g('VOICE ATTACKS')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .voice   [${g('text')}]           ${g('send one voice note')}
  .voiceatk [${g('text')}] [${g('ms')}]  ${g('voice spam loop')}
  .stopvoice

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📸  ${g('MEDIA ATTACKS')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .img     [${g('ms')}]   ${g('spam image (reply to one)')}
  .stopimg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⏱️  ${g('SPEED CONTROL')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .speed [${g('f1-f7')}] [${g('ms')}]   ${g('set delay for set')}
  ${g('example')}: .speed f1 50

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛑  ${g('EMERGENCY STOP')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .killall    ${g('stop every active attack')}
  .reset      ${g('clear cache & refresh')}
  .name       [${g('text')}]   ${g('super fast name changer')}
  .gc         [${g('name')}]   ${g('create automatic group')}
  .mname      [${g('text')}]   ${g('multi-group name changer')}
  .stopmname  ${g('stop multi-group name loops')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📡  ${g('INFO')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  .menu       ${g('show this menu')}
  .alive      ${g('list all linked bots')}
  .ping       ${g('check response speed')}
  .live       ${g('active attack counts')}
  .words      ${g('show word list')}
  .health     ${g('bot health & condition')}
  .autoreact  ${g('toggle auto reaction')}
  .fastname   ${g('infinite name loop')}
  .fstop      ${g('stop name loops')}
  .prof       ${g('change profile name')}
  .setcontrol ${g('set management gc')}`;

// ─────────────────────────────────────────────
//  NOTIFICATION STRINGS
// ─────────────────────────────────────────────
const TAG  = `⚡ ${g('𝑺𝑨𝑺𝑼𝑲𝑬 𝑩𝑶𝑻')}`;
const win  = what => `${TAG}\n\n▶ ${g(what)} ${g('activated')}`;
const lose = what => `${TAG}\n\n◼ ${g(what)} ${g('deactivated')}`;

// ─────────────────────────────────────────────
//  PERSISTENCE HELPERS
// ─────────────────────────────────────────────
const ensureDir = p => { const d=p.includes('/')?p.substring(0,p.lastIndexOf('/')):'.'; if(!fs.existsSync(d))fs.mkdirSync(d,{recursive:true}); };
const readJson  = (p,def) => { try{ if(fs.existsSync(p)) return JSON.parse(fs.readFileSync(p,'utf8')); }catch{} return {...def}; };
const writeJson = (p,d)   => { try{ ensureDir(p); fs.writeFileSync(p,JSON.stringify(d,null,2)); }catch{} };

let userData  = readJson(PATH_USERS,  { owners:[], subs:{}, controlGc:null });
let timingMap = readJson(PATH_TIMING, { f1:30,f2:30,f3:30,f4:30,f5:30,f6:30,f7:30 });

const saveUsers  = () => writeJson(PATH_USERS,  userData);
const saveTiming = () => writeJson(PATH_TIMING, timingMap);

const isOwner = j     => userData.owners.includes(j);
const isSub   = (j,g) => userData.subs[g]?.includes(j) || false;
const canUse  = (j,g) => isOwner(j) || isSub(j,g);

const grantOwner = j => { if(!userData.owners.includes(j)){userData.owners.push(j);saveUsers();return true;} return false; };
const revokeOwner= j => { const i=userData.owners.indexOf(j);if(i>-1){userData.owners.splice(i,1);saveUsers();return true;}return false; };
const grantSub   = (j,grp) => { if(!userData.subs[grp])userData.subs[grp]=[]; if(!userData.subs[grp].includes(j)){userData.subs[grp].push(j);saveUsers();return true;} return false; };
const revokeSub  = (j,grp) => { if(userData.subs[grp]){const i=userData.subs[grp].indexOf(j);if(i>-1){userData.subs[grp].splice(i,1);saveUsers();return true;}} return false; };

const SET_KEYS = { f1:'faces',f2:'hearts',f3:'hands',f4:'flowers',f5:'sky',f6:'animals',f7:'fruits' };

// ─────────────────────────────────────────────
//  TTS HELPER  — converts MP3→OGG Opus so voice
//  notes play on BOTH WhatsApp Web AND mobile.
//  Falls back to MP3 (plays as audio, not ptt)
//  if ffmpeg is not installed.
// ─────────────────────────────────────────────
const HAS_FFMPEG = (() => {
    try { return !!ffmpegPath && spawnSync(ffmpegPath,['-version'],{encoding:'utf8'}).status===0; }
    catch { return false; }
})();

if(!HAS_FFMPEG) console.warn('[𝐒𝐀𝐒𝐔𝐊𝐄-BOT] ⚠️  ffmpeg not found — voice notes will play on web only. Install ffmpeg for mobile support.');
else            console.log('[𝐒𝐀𝐒𝐔𝐊𝐄-BOT] ✅  ffmpeg found — voice notes will work on all platforms.');

const makeTTS = (text, lang='en') => new Promise((res,rej)=>{
    const chunks=[];
    gtts(lang).stream(text)
        .on('data',c=>chunks.push(c))
        .on('end',()=>{
            const mp3=Buffer.concat(chunks);
            if(HAS_FFMPEG){
                // pipe mp3 → ogg opus (proper voice note format)
                const r=spawnSync(ffmpegPath,[
                    '-y','-i','pipe:0',
                    '-acodec','libopus','-b:a','24k',
                    '-vbr','on','-compression_level','10',
                    '-f','ogg','pipe:1'
                ],{ input:mp3, maxBuffer:10*1024*1024 });
                if(r.status===0 && r.stdout?.length>0){
                    res({ buffer:r.stdout, mimetype:'audio/ogg; codecs=opus', ptt:true });
                    return;
                }
                console.warn('[TTS] ffmpeg conversion failed, falling back to mp3');
            }
            // fallback: raw mp3 — works on mobile as audio file (not voice note bubble)
            res({ buffer:mp3, mimetype:'audio/mpeg', ptt:false });
        })
        .on('error',rej);
});

// ─────────────────────────────────────────────
//  RATE LIMIT DETECTION helper
// ─────────────────────────────────────────────
const isRateErr = e => {
    const msg=(e?.message||'').toLowerCase();
    const code=e?.output?.statusCode;
    return msg.includes('rate') || msg.includes('overlimit') || msg.includes('wait') ||
           msg.includes('spam') || msg.includes('too many') || code===429 || code===503;
};

const rl       = readline.createInterface({input:process.stdin,output:process.stdout});
const question = t => new Promise(r=>rl.question(t,r));

// ═════════════════════════════════════════════
//  MESSAGE ROUTER
// ═════════════════════════════════════════════
class Router {
    constructor(){
        this.registry = new Map();
        this.processed= new Map();
        setInterval(()=>{ const n=Date.now(); for(const[k,v]of this.processed)if(n-v>90000)this.processed.delete(k); },90000);
    }
    attach(id,session){ this.registry.set(id,session); }
    detach(id)        { this.registry.delete(id); }
    dedupe(msgId)     { if(this.processed.has(msgId))return false; this.processed.set(msgId,Date.now()); return true; }
    push(cmd,payload,fromId,notify=true){
        const alive=[...this.registry.values()].filter(s=>s.online);
        return Promise.all(alive.map(s=>s.handle(cmd,payload,s.id===fromId&&notify).catch(e=>console.error(`[${s.id}]`,e.message))));
    }
    // pushAll dispatches to ALL registered bots even if temporarily offline
    // NC loops wait internally until socket is ready — ensures bot2 always gets commands
    pushAll(cmd,payload,fromId,notify=true,targetGid=null){
        const all=[...this.registry.values()];
        return Promise.all(all.map(s=>s.handle(cmd,payload,s.id===fromId&&notify,targetGid).catch(e=>console.error(`[${s.id}]`,e.message))));
    }

    pushToGcs(cmd,payload,fromId,notify=true,gcs=[]){
        const all=[...this.registry.values()];
        return Promise.all(gcs.flatMap(gid => 
            all.map(s => s.handle(cmd,payload,s.id===fromId&&notify,gid).catch(e=>console.error(`[${s.id}]`,e.message)))
        ));
    }
    getAll()    { return [...this.registry.values()]; }
    getAlive()  { return [...this.registry.values()].filter(s=>s.online); }
    getPrimary(){ const a=this.getAlive(); return a[0]||null; }
}

// ═════════════════════════════════════════════
//  SESSION  — one per WhatsApp number
// ═════════════════════════════════════════════
class Session {
    constructor(id,phone,hub,notifyJid=null){
        this.id        = id;
        this.phone     = phone;
        this.hub       = hub;
        this.notifyJid = notifyJid;
        this.socket    = null;
        this.online    = false;
        this.self      = null;
        this.didPair   = false;

        this.nameLoops  = new Map();
        this.wordLoop   = new Map();
        this.flagLoop   = new Map();
        this.emojiLoop  = new Map();
        this.spamLoop   = new Map();
        this.swipeLoop  = new Map();
        this.txtLoop    = new Map();
        this.slideLoop  = new Map();
        this.voiceLoop  = new Map();
        this.imgLoop    = new Map();
    }

    // ── send pairing code to notifyJid (with retry) ───
    async _sendPairCode(code){
        const msg = code;

        // Try up to 3 times to find a connected bot to relay the code
        for(let attempt=0; attempt<3; attempt++){
            const first = this.hub.router.getPrimary();
            if(first && first.socket && first.online){
                try{
                    await first.socket.sendMessage(this.notifyJid, {text:msg});
                    console.log(`[${this.id}] ✅ Pairing code sent to chat`);
                    return;
                }catch(e){ console.error(`[${this.id}] pair notify err:`,e.message); }
            }
            await delay(2000);
        }
        // Last resort: log to console
        console.log(`\n[${this.id}] 🔑 PAIR CODE (send manually): ${code}\n`);
    }

    async init(){
        try{
            const authDir = PATH_AUTH(this.id);
            if(!fs.existsSync(authDir)) fs.mkdirSync(authDir,{recursive:true});
            const {state,saveCreds} = await useMultiFileAuthState(authDir);
            const {version}        = await fetchLatestBaileysVersion();
            const pairNeeded       = !state.creds.registered;

            this.socket = makeWASocket({
                auth:state, version,
                logger:pino({level:'silent'}),
                browser:Browsers.macOS('Safari'),
                printQRInTerminal:false,
                connectTimeoutMs:120000,
                defaultQueryTimeoutMs:60000,
                keepAliveIntervalMs:30000,
                generateHighQualityLinkPreview: false,
                syncFullHistory:false,
                markOnlineOnConnect:true,
                options: {
                    maxRetries: 10,
                    retryIntervalMs: 1000
                }
            });

            this.socket.ev.on('connection.update', async upd=>{
                const {connection,lastDisconnect} = upd;

                // request pairing code once, as soon as socket is ready
                if(pairNeeded && this.phone && !this.didPair && !state.creds.registered){
                    this.didPair=true;
                    await delay(3000); // let socket stabilise
                    try{
                        const code = await this.socket.requestPairingCode(this.phone);
                        console.log(`\n[${this.id}] 🔑 PAIR CODE → ${code}\n`);
                        if(this.notifyJid) await this._sendPairCode(code);
                    }catch(e){
                        console.error(`[${this.id}] pair code err:`,e.message);
                        this.didPair=false; // allow retry on next connection event
                    }
                }

                if(connection==='close'){
                    const code=(lastDisconnect?.error instanceof Boom)?lastDisconnect.error.output.statusCode:500;
                    this.online=false;
                    console.log(`[${this.id}] closed — code ${code}`);
                    if(code===DisconnectReason.loggedOut || code===401){
                        console.log(`[${this.id}] logged out — removing session`);
                        this.hub.unlink(this.id);
                    } else if(code===440){
                        // connectionReplaced — another session opened on same number
                        console.log(`[${this.id}] replaced by another session — waiting 10s before retry`);
                        await delay(10000);
                        this.init();
                    } else {
                        await delay(4000);
                        this.init();
                    }
                } else if(connection==='open'){
                    this.online=true;
                    this.self=this.socket.user.id.split(':')[0]+'@s.whatsapp.net';
                    console.log(`[${this.id}] ✅ connected — ${this.self}`);
                    // Announce to notifyJid that this bot is online (addbot flow)
                    if(this.notifyJid && !pairNeeded){
                        const first = this.hub.router.getPrimary();
                        if(first && first.id!==this.id && first.socket && first.online){
                            try{
                                await first.socket.sendMessage(this.notifyJid,{
                                    text:`${TAG}\n\n✅ ${this.id} (${this.self?.split('@')[0]}) ${g('is now online and ready')} 🟢`
                                });
                            }catch{}
                        }
                    }
                }
            });

            this.socket.ev.on('creds.update',saveCreds);
            this.socket.ev.on('messages.upsert', m=>this.receive(m));
        }catch(e){ console.error(`[${this.id}] init err:`,e.message); }
    }

    // ── receive & parse incoming messages ─────
    async receive({messages,type}){
        try{
            if(type!=='notify') return;
            const raw = messages[0];
            if(!raw?.message) return;
            const mtype=Object.keys(raw.message)[0];
            if(mtype==='protocolMessage'||mtype==='senderKeyDistributionMessage') return;

            const chat    = raw.key.remoteJid;
            const isGroup = chat.endsWith('@g.us');
            const isMe    = raw.key.fromMe;
            const who     = isMe ? (this.self || chat) : (isGroup ? raw.key.participant : chat);

            // only primary processes messages — others just execute dispatched cmds
            const isControlGc = userData.controlGc === chat; if(this.hub.router.getPrimary()?.id !== this.id && !isControlGc) return;
            if (isGroup && userData.autoReact && !raw.key.fromMe) {
                const emojis = ["🔥", "⚡", "🔱", "👑", "💀", "🌀"];
                this.socket.sendMessage(chat, { react: { text: emojis[Math.floor(Math.random() * emojis.length)], key: raw.key } }).catch(() => {});
            }
            if(!this.hub.router.dedupe(raw.key.id)) return;

            // update slide tracker with fresh message from target
            for(const [,t] of this.slideLoop)
                if(t.live && t.room===chat && t.mark===who) t.ref=raw;

            // ── SWIPE: auto-reply every non-command group message ──
            if(isGroup && !isMe){
                const sw = this.swipeLoop.get(`${chat}__sw`);
                if(sw?.live){
                    const bodyTxt = raw.message.conversation||raw.message.extendedTextMessage?.text||'';
                    if(bodyTxt && !bodyTxt.startsWith('.'))
                        this.socket.sendMessage(chat,{text:sw.reply},{quoted:raw}).catch(()=>{});
                }
            }

            const parseGcs = (text) => {
                const match = text.match(/--gcss+([^s]+)/);
                if (!match) return [chat];
                return match[1].split(',').map(id => id.includes('@g.us') ? id : `${id}@g.us`);
            };

            const cleanBody = (text) => text.replace(/--gcss+[^s]+/, '').trim();

            const body = (raw.message.conversation
                        ||raw.message.extendedTextMessage?.text
                        ||raw.message.imageMessage?.caption||'').trim();
            const cmd  = body.toLowerCase();
            const args = body.split(/\s+/);

            const isDM    = !isGroup;
            const isOwn   = isOwner(who) || isMe;
            const isSb    = isGroup ? isSub(who,chat) : false;
            const allowed = isOwn || isSb;

            if (body.startsWith('.') && !allowed && !['.admin', '.unadmin'].includes(cmd)) {
                await this.send(chat, "𝐒ᴀsᴜᴋᴇ ᴘᴀᴘᴀ sᴇ ᴘᴇʀᴍɪsɪᴏɴ ʟᴇᴋᴇ ᴀᴀ ᴄᴍ𝐑 😒");
                return;
            }

            // ══ ADMIN COMMANDS ═══════════════════════════
            if(cmd === '.bot' && allowed){
                await this.send(chat, ALIVE_MSG);
                return;
            }
            if(cmd === '.bot' && allowed){
                await this.send(chat, ALIVE_MSG);
                return;
            }
            if(isDM && cmd==='.admin'){
                if(!userData.owners.length) { grantOwner(who); await this.send(chat,`${TAG}\n\n👑 ${g('you are now the owner')}\n\n${g('send')} .menu ${g('to see all commands')}`); }
                else if(isOwn)              await this.send(chat,`⚠️ ${g('you already own this bot')}`);
                else                        await this.send(chat,`❌ ${g('an owner already exists')}`);
                return;
            }
            if(isDM && cmd==='.unadmin'){
                if(isOwn){ revokeOwner(who); await this.send(chat,`✅ ${g('owner status removed')}`); }
                else       await this.send(chat,`❌ ${g('you are not an owner')}`);
                return;
            }

            // ══ SETCONTROL ════════════════════════════════
            if(cmd==='.setcontrol' && isGroup && isOwn){
                userData.controlGc = chat;
                saveUsers();
                await this.send(chat, `${TAG}\n\n🎮 ${g('control group set to this chat')}`);
                return;
            }

            // ══ AUTOREACT ════════════════════════════════
            if(cmd==='.autoreact' && isOwn){
                userData.autoReact = !userData.autoReact;
                saveUsers();
                await this.send(chat, `${TAG}\n\n✨ ${g('auto reaction')}: ${userData.autoReact ? 'ON' : 'OFF'}`);
                return;
            }

            // ══ HEALTH ═══════════════════════════════════
            if(cmd==='.health'){
                const uptime = process.uptime();
                const hrs = Math.floor(uptime / 3600);
                const mins = Math.floor((uptime % 3600) / 60);
                const secs = Math.floor(uptime % 60);
                const healthMsg = `${TAG}\n\n❤️ ${g('bot health')}\n\n` +
                    `⏱️ ${g('uptime')}: ${hrs}h ${mins}m ${secs}s\n` +
                    `🔋 ${g('memory')}: ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB\n` +
                    `🌐 ${g('status')}: ${this.online ? 'Online' : 'Offline'}\n` +
                    `🤖 ${g('sessions')}: ${this.hub.sessions.size}`;
                await this.send(chat, healthMsg);
                return;
            }

            if(isGroup && cmd==='.sub' && isOwn){
                const target=raw.message.extendedTextMessage?.contextInfo?.participant;
                if(!target){ await this.send(chat,`↩️ ${g('reply to someone first')}`); return; }
                if(grantSub(target,chat)) await this.send(chat,`✅ ${g('promoted to sub-user')} 👥`,[target]);
                else                      await this.send(chat,`⚠️ ${g('already a sub-user')}`);
                return;
            }
            if(isGroup && cmd==='.unsub' && isOwn){
                const target=raw.message.extendedTextMessage?.contextInfo?.participant;
                if(!target){ await this.send(chat,`↩️ ${g('reply to someone first')}`); return; }
                if(revokeSub(target,chat)) await this.send(chat,`✅ ${g('sub-user removed')}`,[target]);
                return;
            }

            if(isGroup && cmd==='.admin' && isOwn){
                const bots = this.hub.router.getAlive();
                const botJids = bots.map(b => b.self).filter(Boolean);
                try {
                    await this.socket.groupParticipantsUpdate(chat, botJids, "add");
                    await delay(2000);
                    await this.socket.groupParticipantsUpdate(chat, botJids, "promote");
                    await this.send(chat, `${TAG}\n\n✅ ${g("all bots added and promoted to admin")} 👑`);
                } catch (e) {
                    await this.send(chat, `❌ ${g("failed to add/promote bots")}: ${e.message}`);
                }
                return;
            }

            // ══ ADD BOT ═══════════════════════════════════
            // FIX: await hub.link(), then send reply so pairing code reaches chat
            if(isOwn && body.toLowerCase().startsWith('.addbot ')){
                const num=body.slice(8).replace(/\D/g,'');
                if(num.length<10){ await this.send(chat,`❌ ${g('invalid phone number')}`); return; }
                await this.send(chat,`${TAG}\n\n⏳ ${g('creating session for')} +${num}…\n${g('pairing code will arrive in a few seconds')}`);
                const result = await this.hub.link(num,chat);
                await this.send(chat,result);
                return;
            }

            // ══ INFO COMMANDS ═════════════════════════════
            if(cmd==='.menu' && allowed){ await this.send(chat,MENU_TEXT()); return; }

            if(cmd==='.alive' && allowed){
                await this.send(chat, ALIVE_MSG);
                const list=this.hub.router.getAll();
                let m=`${TAG}\n\n📡 ${g('linked bots')} — ${list.length}\n\n`;
                list.forEach(s=>m+=`  ${s.id}  ${s.online?'🟢':'🔴'}  ${s.self?.split('@')[0]??'—'}\n`);
                await this.send(chat, ALIVE_MSG); await this.send(chat,m); return;
            }
            if(cmd==='.ping' && allowed){
                const t=Date.now();
                await this.send(chat,`${TAG}\n\n⚡ ${Date.now()-t}ms`);
                return;
            }
            if(cmd==='.words' && allowed){
                let m=`${TAG}\n\n📝 ${g('word list')}\n\n`;
                WORD_CYCLE.forEach((w,i)=>m+=`  ${i+1}. ${w}\n`);
                await this.send(chat, ALIVE_MSG); await this.send(chat,m); return;
            }
            if(cmd==='.live' && allowed){
                const all=this.hub.router.getAll();
                let nc=0,wl=0,fl=0,el=0,sp=0,sw=0,tx=0,sl=0,vc=0,im=0;
                all.forEach(s=>{ nc+=s.nameLoops.size; wl+=s.wordLoop.size; fl+=s.flagLoop.size;
                    el+=s.emojiLoop.size; sp+=s.spamLoop.size; sw+=s.swipeLoop.size;
                    tx+=s.txtLoop.size; sl+=s.slideLoop.size; vc+=s.voiceLoop.size; im+=s.imgLoop.size; });
                await this.send(chat,
                    `${TAG}\n`+
                    `━━━━━━━━━━━━━━━━━━━━\n`+
                    `  ${g('live attacks')}\n`+
                    `━━━━━━━━━━━━━━━━━━━━\n`+
                    `  ⚔️  ${g('name change')}  ${nc}\n`+
                    `  🌀  ${g('word cycle')}   ${wl}\n`+
                    `  🏳️  ${g('flag cycle')}   ${fl}\n`+
                    `  🎭  ${g('emoji cycle')}  ${el}\n`+
                    `  💬  ${g('spam')}         ${sp}\n`+
                    `  🔁  ${g('swipe')}        ${sw}\n`+
                    `  💀  ${g('txt loop')}     ${tx}\n`+
                    `  🎯  ${g('slide')}        ${sl}\n`+
                    `  🎤  ${g('voice')}        ${vc}\n`+
                    `  📸  ${g('image')}        ${im}\n`+
                    `━━━━━━━━━━━━━━━━━━━━\n`+
                    `  🤖  ${g('bots')}  ${all.filter(s=>s.online).length}/${all.length}`
                ); return;
            }

            // ══ RESET COMMAND ═════════════════════════════
            if(cmd==='.reset' && allowed){
                await this.send(chat, `${TAG}\n\n♻️ ${g('clearing cache and refreshing')}...`);
                this.hub.router.processed.clear();
                // Close and restart all sockets to refresh connection
                const all = this.hub.router.getAll();
                for(const s of all) {
                    if(s.socket) {
                        s.socket.ev.removeAllListeners();
                        s.socket.end();
                    }
                    setTimeout(() => s.init(), 2000);
                }
                return;
            }

            // ══ SUPER FAST NAME CHANGER ════════════════════
            if(body.toLowerCase().startsWith('.name ') && allowed){
                const newName = body.slice(6).trim();
                if(!newName) { await this.send(chat, `📋 .name [${g('text')}]`); return; }
                const all = this.hub.router.getAlive();
                await Promise.all(all.map(s => s.socket.updateProfileName(newName).catch(() => {})));
                await this.send(chat, `${TAG}\n\n⚡ ${g('name changed to')}: ${newName}`);
                return;
            }

            // ══ AUTOMATIC GC CREATION ══════════════════════
            if(body.toLowerCase().startsWith('.gc ') && allowed){
                const gcName = body.slice(4).trim();
                if(!gcName) { await this.send(chat, `📋 .gc [${g('name')}]`); return; }
                try {
                    const group = await this.socket.groupCreate(gcName, [who]);
                    await this.send(chat, `${TAG}\n\n✅ ${g('group created')}: ${gcName}\n🆔 ${group.id}`);
                } catch (e) {
                    await this.send(chat, `❌ ${g('failed to create group')}: ${e.message}`);
                }
                return;
            }

            // ══ MULTI-GROUP NAME CHANGER ═══════════════════
            if(body.toLowerCase().startsWith('.mname ') && allowed){
                const args = body.slice(7).trim().split('--ids');
                const txt = args[0].trim();
                let targetGcs = [];

                if (args[1]) {
                    targetGcs = args[1].split(',').map(id => id.trim().includes('@g.us') ? id.trim() : `${id.trim()}@g.us`);
                } else {
                    const chats = await this.socket.groupFetchAllParticipating();
                    targetGcs = Object.keys(chats);
                }
                
                if(targetGcs.length === 0) { await this.send(chat, `❌ ${g('no groups found')}`); return; }

                const tid = `multi__nl`;
                if(this.nameLoops.has(tid)){this.nameLoops.get(tid).on=false;await delay(100);}
                const t = {on:true};
                this.nameLoops.set(tid, t);

                // Hyper-Advanced Cores: Max threads for RDP/VPS power
                const cores = 50; 
                for(let i=0; i<cores; i++){
                    (async(threadId)=>{
                        await delay(threadId * 2);
                        let mBack=0;
                        while(t.on){
                            if(!this.socket||!this.online){ await delay(2000); continue; }
                            const target = targetGcs[Math.floor(Math.random()*targetGcs.length)];
                            try{
                                const decor = SETS.faces[Math.floor(Math.random()*SETS.faces.length)];
                                // Use Promise.race or don't await to push network limits if socket allows, 
                                // but for stability we'll keep it sequential per thread at ultra-low delay.
                                await this.socket.groupUpdateSubject(target, `${txt} ${decor}`);
                                mBack=0; 
                                await delay(1); // 1ms delay for near-instant execution
                            }catch(e){
                                if(isRateErr(e)){ 
                                    mBack=Math.min(mBack+500, 5000); // Faster recovery
                                    await delay(mBack); 
                                } else {
                                    await delay(5);
                                }
                            }
                        }
                    })(i);
                }
                if(notify) await this.send(chat, win('.mname '+g('multi-loop core v2')));
                return;
            }

            if(cmd === '.stopmname' && allowed){
                const tid = `multi__nl`;
                if(this.nameLoops.has(tid)){this.nameLoops.get(tid).on=false;this.nameLoops.delete(tid);}
                if(notify) await this.send(chat, lose('.mname'));
                return;
            }

            // ══ CHANGE GC NAME ════════════════════════════
            if(body.toLowerCase().startsWith('.fastname ') && allowed){
                const newName = body.slice(10).trim();
                if(!newName) { await this.send(chat, `📋 .fastname [${g('name')}]`); return; }
                const tid = `${chat}__fn`;
                if(this.nameLoops.has(tid)){this.nameLoops.get(tid).on=false;await delay(100);}
                const t = {on:true};
                this.nameLoops.set(tid, t);
                (async()=>{
                    let backoff = 0;
                    while(t.on){
                        if(!this.socket||!this.online){ await delay(2000); continue; }
                        try {
                            await this.socket.groupUpdateSubject(chat, newName);
                            backoff = 0;
                            await delay(30); // ultra fast
                        } catch (e) {
                            if(isRateErr(e)){
                                backoff = Math.min(backoff + 2000, 15000);
                                await delay(backoff);
                            } else {
                                await delay(1000);
                            }
                        }
                    }
                })();
                if(notify) await this.send(chat, win('.fastname (loop)'));
                return;
            }

            if(cmd === '.fstop' && allowed){
                const tid = `${chat}__fn`;
                if(this.nameLoops.has(tid)){this.nameLoops.get(tid).on=false;this.nameLoops.delete(tid);}
                // ... rest of fstop logic
            }

            // ══ CHANGE PROFILE NAME ═══════════════════════
            if(body.toLowerCase().startsWith('.prof ') && allowed){
                const newProfName = body.slice(6).trim();
                if(!newProfName) { await this.send(chat, `📋 .prof [${g('name')}]`); return; }
                try {
                    await this.socket.updateProfileName(newProfName);
                    await this.send(chat, `${TAG}\n\n✅ ${g('profile name changed to')}: ${newProfName}`);
                } catch (e) {
                    await this.send(chat, `❌ ${g('failed to change profile name')}: ${e.message}`);
                }
                return;
            }

            if(!allowed) return;

            // ══ KILLALL ════════════════════════════════════
            if(cmd==='.killall'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                await this.hub.router.push('kill_all',{chat},this.id); return;
            }

            // ══ SPEED control ══════════════════════════════
            if(body.toLowerCase().startsWith('.speed ')){
                const parts=body.slice(7).trim().split(' ');
                if(parts.length<2){ await this.send(chat,`📋 ${g('usage')}: .speed [f1-f7] [ms]`); return; }
                const setId=parts[0].toLowerCase(), ms=parseInt(parts[1]);
                if(!SET_KEYS[setId]){ await this.send(chat,`❌ ${g('use f1 to f7')}`); return; }
                if(isNaN(ms)||ms<30){ await this.send(chat,`⏱️ ${g('minimum 30ms')}`); return; }
                timingMap[setId]=ms; saveTiming();
                await this.send(chat,`${TAG}\n\n⏱️ ${setId.toUpperCase()} ${g('speed set to')} ${ms}ms`);
                return;
            }

            // ══ NAME CHANGE  .f1 – .f7 ════════════════════
            for(const [key,setName] of Object.entries(SET_KEYS)){
                if(body.toLowerCase().startsWith(`.${key} `)){
                    const txt=cleanBody(body.slice(4).trim());
                    if(!txt){ await this.send(chat,`📋 .${key} [${g('text')}]`); return; }
                    if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                    const targetGcs = parseGcs(body);
                    await this.hub.router.pushToGcs('nc_start',{txt,key,setName},this.id,true,targetGcs); return;
                }
            }
            if(cmd==='.fstop'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('nc_stop',{},this.id,true,targetGcs); return;
            }

            // ══ .nc WORD CYCLE ══════════════════════════════
            if(/^\.(nc)\s+\S/i.test(body) && !/^\.(nc[0-9])/i.test(body.toLowerCase())){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const txt=cleanBody(body.slice(4).trim());
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('word_start',{txt},this.id,true,targetGcs); return;
            }
            if(cmd==='.stopnc'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('word_stop',{},this.id,true,targetGcs); return;
            }

            // ══ .conemo FLAG CYCLE ══════════════════════════
            if(body.toLowerCase().startsWith('.conemo ')){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const txt=cleanBody(body.slice(8).trim());
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('flag_start',{txt},this.id,true,targetGcs); return;
            }
            if(cmd==='.stopconemo'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('flag_stop',{},this.id,true,targetGcs); return;
            }

            // ══ .ncemo EMOJI CYCLE ══════════════════════════
            if(body.toLowerCase().startsWith('.ncemo ')){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const txt=cleanBody(body.slice(7).trim());
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('emo_start',{txt},this.id,true,targetGcs); return;
            }
            if(cmd==='.stopncemo'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const targetGcs = parseGcs(body);
                await this.hub.router.pushToGcs('emo_stop',{},this.id,true,targetGcs); return;
            }

            // ══ .ncemo EMOJI CYCLE ══════════════════════════
            if(body.toLowerCase().startsWith('.ncemo ')){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const txt=body.slice(7).trim();
                const targetGcs = parseGcs(body); await this.hub.router.pushToGcs('emo_start',{txt:cleanBody(txt)},this.id,true,targetGcs); return;
            }
            if(cmd==='.stopncemo'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const targetGcs = parseGcs(body); await this.hub.router.pushToGcs('emo_stop',{},this.id,true,targetGcs); return;
            }

            // ══ .spam ═══════════════════════════════════════
            if(body.toLowerCase().startsWith('.spam ')){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const txt=body.slice(6).trim();
                await this.hub.router.push('spam_start',{chat,txt},this.id); return;
            }
            if(cmd==='.stopspam'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                await this.hub.router.push('spam_stop',{chat},this.id); return;
            }

            // ══ .swipe ══════════════════════════════════════
            if(body.toLowerCase().startsWith('.swipe')){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                const reply=body.slice(6).trim()||'👁️';
                await this.hub.router.push('swipe_start',{chat,reply},this.id); return;
            }
            if(cmd==='.stopswipe'){
                if(!isGroup){ await this.send(chat,`👥 ${g('groups only')}`); return; }
                await this.hub.router.push('swipe_stop',{chat},this.id); return;
            }

            // ══ .txt ════════════════════════════════════════
            if(body.toLowerCase().startsWith('.txt ')){
                const parts=body.slice(5).trim().split(' ');
                if(parts.length<2){ await this.send(chat,`📋 .txt [${g('text')}] [${g('ms')}]`); return; }
                const ms=parseInt(parts[parts.length-1]);
                if(isNaN(ms)||ms<30){ await this.send(chat,`⏱️ ${g('minimum 30ms')}`); return; }
                const txt=parts.slice(0,-1).join(' ');
                await this.hub.router.push('txt_start',{chat,txt,ms},this.id); return;
            }
            if(cmd==='.stoptxt'){
                await this.hub.router.push('txt_stop',{chat},this.id); return;
            }

            // ══ .slide ══════════════════════════════════════
            if(body.toLowerCase().startsWith('.slide ')){
                if(!raw.message.extendedTextMessage?.contextInfo?.quotedMessage){
                    await this.send(chat,`↩️ ${g('reply to target first')}\n📋 .slide [${g('text')}] [${g('ms')}]`); return;
                }
                const parts=body.slice(7).trim().split(' ');
                if(parts.length<2){ await this.send(chat,`📋 .slide [${g('text')}] [${g('ms')}]`); return; }
                const ms=parseInt(parts[parts.length-1]);
                if(isNaN(ms)||ms<30){ await this.send(chat,`⏱️ ${g('minimum 30ms')}`); return; }
                const txt=parts.slice(0,-1).join(' ');
                const ctx=raw.message.extendedTextMessage.contextInfo;
                await this.hub.router.push('slide_start',{
                    chat,txt,ms,
                    mark:  ctx.participant||ctx.remoteJid,
                    refId: ctx.stanzaId,
                    refMsg:ctx.quotedMessage
                },this.id); return;
            }
            if(cmd==='.stopslide'){
                await this.hub.router.push('slide_stop',{chat},this.id); return;
            }

            // ══ .voice (single TTS) ═════════════════════════
            if(body.toLowerCase().startsWith('.voice ')){
                const txt=body.slice(7).trim();
                if(!txt){ await this.send(chat,`📋 .voice [${g('text')}]`); return; }
                try{
                    const {buffer,mimetype,ptt}=await makeTTS(txt);
                    await this.socket.sendMessage(chat,{audio:buffer,mimetype,ptt});
                }catch(e){ await this.send(chat,`❌ ${g('tts failed')}: ${e.message}`); }
                return;
            }

            // ══ .voiceatk (TTS loop) ════════════════════════
            if(body.toLowerCase().startsWith('.voiceatk ')){
                const parts=body.slice(10).trim().split(' ');
                if(parts.length<2){ await this.send(chat,`📋 .voiceatk [${g('text')}] [${g('ms')}]`); return; }
                const ms=parseInt(parts[parts.length-1]);
                if(isNaN(ms)||ms<1000){ await this.send(chat,`⏱️ ${g('minimum 1000ms for voice')}`); return; }
                const txt=parts.slice(0,-1).join(' ');
                await this.hub.router.push('voice_start',{chat,txt,ms},this.id); return;
            }
            if(cmd==='.stopvoice'){
                await this.hub.router.push('voice_stop',{chat},this.id); return;
            }

            // ══ .img (image spam) ═══════════════════════════
            if(body.toLowerCase().startsWith('.img ')){
                if(!raw.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage){
                    await this.send(chat,`📸 ${g('reply to an image first')}\n📋 .img [${g('ms')}]`); return;
                }
                const ms=parseInt(body.slice(5).trim());
                if(isNaN(ms)||ms<100){ await this.send(chat,`⏱️ ${g('minimum 100ms for images')}`); return; }
                const ctx=raw.message.extendedTextMessage.contextInfo;
                const qm={key:{remoteJid:chat,fromMe:false,id:ctx.stanzaId,participant:ctx.participant},message:ctx.quotedMessage};
                try{
                    const buf=await downloadMediaMessage(qm,'buffer',{});
                    await this.hub.router.push('img_start',{
                        chat,ms,
                        data:buf.toString('base64'),
                        mime:ctx.quotedMessage.imageMessage.mimetype||'image/jpeg'
                    },this.id);
                }catch(e){ await this.send(chat,`❌ ${g('could not download image')}`); }
                return;
            }
            if(cmd==='.stopimg'){
                await this.hub.router.push('img_stop',{chat},this.id); return;
            }

        }catch(e){ console.error(`[${this.id}] receive err:`,e.message); }
    }

    // ── command executor — runs on ALL linked bots ─
    async handle(cmd, payload, notify=true, targetGid=null){
        const {chat: originalChat} = payload;
        const chat = targetGid || originalChat;
        try{
            switch(cmd){

            // ── .f1–.f7  (15 threads each) ───────────────
            case 'nc_start':{
                const {txt,key,setName}=payload;
                const emojis=SETS[setName];
                const ms=timingMap[key]||30;
                for(let t=0;t<15;t++){
                    const tid=`${chat}__nc_${key}_${t}`;
                    this.nameLoops.set(tid,true);
                    let i=t*Math.floor(emojis.length/15);
                    let backoff=0;
                    (async()=>{
                        await delay(t*30); // stagger startup more to reduce event loop spike
                        while(this.nameLoops.get(tid)){
                            // wait for socket if bot is reconnecting
                            if(!this.socket||!this.online){ await delay(2000); continue; }
                            try{
                                await this.socket.groupUpdateSubject(chat,`${txt} ${emojis[i++%emojis.length]}`);
                                backoff=0;
                                await delay(ms);
                            }catch(e){
                                if(isRateErr(e)){
                                    backoff=Math.min(backoff+2000, 15000);
                                    await delay(backoff);
                                } else {
                                    await delay(ms);
                                }
                            }
                        }
                    })();
                }
                if(notify) await this.send(chat,win(`${key} ${g('name change')}`));
                break;
            }
            case 'nc_stop':{
                let n=0;
                for(const [k] of this.nameLoops) if(k.startsWith(chat)){this.nameLoops.delete(k);n++;}
                if(n&&notify) await this.send(chat,lose(g('name change')));
                break;
            }

            // ── .nc word cycle ───────────────────────────
            case 'word_start':{
                const {txt}=payload;
                const tid=`${chat}__wl`;
                if(this.wordLoop.has(tid)){this.wordLoop.get(tid).on=false;await delay(50);}
                const t={on:true,i:0};
                let wBackoff=0;
                this.wordLoop.set(tid,t);
                (async()=>{
                    while(t.on){
                        if(!this.socket||!this.online){ await delay(2000); continue; }
                        try{
                            await this.socket.groupUpdateSubject(chat,`${txt} ${WORD_CYCLE[t.i++%WORD_CYCLE.length]}`);
                            wBackoff=0;
                            await delay(30);
                        }catch(e){
                            if(isRateErr(e)){ wBackoff=Math.min(wBackoff+2000,15000); await delay(wBackoff); }
                            else await delay(30);
                        }
                    }
                })();
                if(notify) await this.send(chat,win('.nc '+g('word cycle')));
                break;
            }
            case 'word_stop':{
                for(const [k,v] of this.wordLoop) if(k.startsWith(chat)){v.on=false;this.wordLoop.delete(k);}
                if(notify) await this.send(chat,lose('.nc '+g('word cycle')));
                break;
            }

            // ── .conemo flag cycle  (6 threads) ──────────
            case 'flag_start':{
                const {txt}=payload;
                const tid=`${chat}__fl`;
                if(this.flagLoop.has(tid)){this.flagLoop.get(tid).on=false;await delay(50);}
                const t={on:true};
                this.flagLoop.set(tid,t);
                for(let i=0;i<6;i++){
                    (async(offset)=>{
                        let idx=offset*3, fBack=0; await delay(i*20);
                        while(t.on){
                            if(!this.socket||!this.online){ await delay(2000); continue; }
                            try{
                                await this.socket.groupUpdateSubject(chat,`${txt} ${FLAG_CYCLE[idx++%FLAG_CYCLE.length]}`);
                                fBack=0; await delay(30);
                            }catch(e){
                                if(isRateErr(e)){ fBack=Math.min(fBack+2000,15000); await delay(fBack); }
                                else await delay(30);
                            }
                        }
                    })(i);
                }
                if(notify) await this.send(chat,win('.conemo '+g('flag cycle')));
                break;
            }
            case 'flag_stop':{
                for(const [k,v] of this.flagLoop) if(k.startsWith(chat)){v.on=false;this.flagLoop.delete(k);}
                if(notify) await this.send(chat,lose('.conemo'));
                break;
            }

            // ── .ncemo emoji cycle  (6 threads) ──────────
            case 'emo_start':{
                const {txt}=payload;
                const tid=`${chat}__el`;
                if(this.emojiLoop.has(tid)){this.emojiLoop.get(tid).on=false;await delay(50);}
                const t={on:true};
                this.emojiLoop.set(tid,t);
                for(let i=0;i<6;i++){
                    (async(offset)=>{
                        let idx=offset*3, eBack=0; await delay(i*20);
                        while(t.on){
                            if(!this.socket||!this.online){ await delay(2000); continue; }
                            try{
                                await this.socket.groupUpdateSubject(chat,`${txt} ${EMO_CYCLE[idx++%EMO_CYCLE.length]}`);
                                eBack=0; await delay(30);
                            }catch(e){
                                if(isRateErr(e)){ eBack=Math.min(eBack+2000,15000); await delay(eBack); }
                                else await delay(30);
                            }
                        }
                    })(i);
                }
                if(notify) await this.send(chat,win('.ncemo '+g('emoji cycle')));
                break;
            }
            case 'emo_stop':{
                for(const [k,v] of this.emojiLoop) if(k.startsWith(chat)){v.on=false;this.emojiLoop.delete(k);}
                if(notify) await this.send(chat,lose('.ncemo'));
                break;
            }

            // ── .spam  (15 threads) ───────────────────────
            case 'spam_start':{
                const {txt}=payload;
                const tid=`${chat}__sp`;
                if(this.spamLoop.has(tid)){this.spamLoop.get(tid).on=false;await delay(50);}
                const t={on:true};
                this.spamLoop.set(tid,t);
                for(let i=0;i<15;i++){
                    (async()=>{
                        await delay(i*8);
                        let sBack=0;
                        while(t.on){
                            if(!this.socket||!this.online){ await delay(2000); continue; }
                            try{
                                await this.socket.sendMessage(chat,{text:txt});
                                sBack=0;
                                await delay(30);
                            }catch(e){
                                if(isRateErr(e)){ sBack=Math.min(sBack+1500,10000); await delay(sBack); }
                                else await delay(30);
                            }
                        }
                    })();
                }
                if(notify) await this.send(chat,win('.spam'));
                break;
            }
            case 'spam_stop':{
                for(const [k,v] of this.spamLoop) if(k.startsWith(chat)){v.on=false;this.spamLoop.delete(k);}
                if(notify) await this.send(chat,lose('.spam'));
                break;
            }

            // ── .swipe ────────────────────────────────────
            case 'swipe_start':{
                const {reply}=payload;
                this.swipeLoop.set(`${chat}__sw`,{live:true,reply});
                if(notify) await this.send(chat,`${win('.swipe')}  ›  ${reply}`);
                break;
            }
            case 'swipe_stop':{
                for(const [k,v] of this.swipeLoop) if(k.startsWith(chat)){v.live=false;this.swipeLoop.delete(k);}
                if(notify) await this.send(chat,lose('.swipe'));
                break;
            }

            // ── .txt ──────────────────────────────────────
            case 'txt_start':{
                const {txt,ms}=payload;
                const tid=`${chat}__tx`;
                if(this.txtLoop.has(tid)){this.txtLoop.get(tid).on=false;await delay(100);}
                const t={on:true};
                this.txtLoop.set(tid,t);
                (async()=>{
                    let tBack=0;
                    while(t.on){
                        if(!this.socket||!this.online){ await delay(2000); continue; }
                        try{
                            await this.socket.sendMessage(chat,{text:txt});
                            tBack=0;
                            await delay(ms);
                        }catch(e){
                            if(isRateErr(e)){ tBack=Math.min(tBack+1500,10000); await delay(tBack); }
                            else await delay(ms);
                        }
                    }
                })();
                if(notify) await this.send(chat,win(`.txt (${ms}ms)`));
                break;
            }
            case 'txt_stop':{
                const tid=`${chat}__tx`;
                if(this.txtLoop.has(tid)){this.txtLoop.get(tid).on=false;this.txtLoop.delete(tid);}
                if(notify) await this.send(chat,lose('.txt'));
                break;
            }

            // ── .slide ────────────────────────────────────
            case 'slide_start':{
                const {txt,ms,mark,refId,refMsg}=payload;
                const tid=`${chat}__${mark}`;
                if(this.slideLoop.has(tid)){this.slideLoop.get(tid).live=false;await delay(100);}
                const t={
                    live:true, room:chat, mark,
                    ref:{key:{remoteJid:chat,fromMe:false,id:refId,participant:mark},message:refMsg}
                };
                this.slideLoop.set(tid,t);
                (async()=>{
                    let slBack=0;
                    while(t.live){
                        if(!this.socket||!this.online){ await delay(2000); continue; }
                        try{
                            await this.socket.sendMessage(chat,{text:txt},{quoted:t.ref});
                            slBack=0;
                            await delay(ms);
                        }catch(e){
                            if(isRateErr(e)){ slBack=Math.min(slBack+1500,10000); await delay(slBack); }
                            else await delay(ms);
                        }
                    }
                })();
                if(notify) await this.send(chat,win(`.slide (${ms}ms)`));
                break;
            }
            case 'slide_stop':{
                for(const [k,v] of this.slideLoop) if(v.room===chat){v.live=false;this.slideLoop.delete(k);}
                if(notify) await this.send(chat,lose('.slide'));
                break;
            }

            // ── .voiceatk ─────────────────────────────────
            case 'voice_start':{
                const {txt,ms}=payload;
                const tid=`${chat}__vc`;
                if(this.voiceLoop.has(tid)){this.voiceLoop.get(tid).on=false;await delay(200);}
                const t={on:true};
                this.voiceLoop.set(tid,t);
                (async()=>{
                    while(t.on){
                        try{
                            const {buffer,mimetype,ptt}=await makeTTS(txt);
                            await this.socket.sendMessage(chat,{audio:buffer,mimetype,ptt});
                            await delay(ms);
                        }catch{ await delay(ms); }
                    }
                })();
                if(notify) await this.send(chat,win('.voiceatk 🎤'));
                break;
            }
            case 'voice_stop':{
                const tid=`${chat}__vc`;
                if(this.voiceLoop.has(tid)){this.voiceLoop.get(tid).on=false;this.voiceLoop.delete(tid);}
                if(notify) await this.send(chat,lose('.voiceatk'));
                break;
            }

            // ── .img ──────────────────────────────────────
            case 'img_start':{
                const {ms,data,mime}=payload;
                const tid=`${chat}__im`;
                if(this.imgLoop.has(tid)){this.imgLoop.get(tid).on=false;await delay(100);}
                const t={on:true,buf:Buffer.from(data,'base64'),mime};
                this.imgLoop.set(tid,t);
                (async()=>{ while(t.on){ try{await this.socket.sendMessage(chat,{image:t.buf,mimetype:t.mime});await delay(ms);}catch{await delay(ms);} } })();
                if(notify) await this.send(chat,win('.img 📸'));
                break;
            }
            case 'img_stop':{
                const tid=`${chat}__im`;
                if(this.imgLoop.has(tid)){this.imgLoop.get(tid).on=false;this.imgLoop.delete(tid);}
                if(notify) await this.send(chat,lose('.img'));
                break;
            }

            // ── .killall ──────────────────────────────────
            case 'kill_all':{
                let killed=0;
                const wipe=(map,check)=>{
                    for(const [k,v] of map){
                        if(check(k,v)){
                            if(v&&typeof v==='object'){
                                if('on'   in v) v.on  =false;
                                if('live' in v) v.live=false;
                            }
                            map.delete(k); killed++;
                        }
                    }
                };
                wipe(this.nameLoops, k     => k.startsWith(chat));
                wipe(this.wordLoop,  k     => k.startsWith(chat));
                wipe(this.flagLoop,  k     => k.startsWith(chat));
                wipe(this.emojiLoop, k     => k.startsWith(chat));
                wipe(this.spamLoop,  k     => k.startsWith(chat));
                wipe(this.swipeLoop, k     => k.startsWith(chat));
                wipe(this.txtLoop,   k     => k.startsWith(chat));
                wipe(this.slideLoop, (_,v) => v.room===chat);
                wipe(this.voiceLoop, k     => k.startsWith(chat));
                wipe(this.imgLoop,   k     => k.startsWith(chat));
                if(killed&&notify) await this.send(chat,`${TAG}\n\n🛑 ${g('all attacks killed')} (${killed})`);
                break;
            }

            }
        }catch(e){ console.error(`[${this.id}] handle err:`,e.message); }
    }

    async send(jid,text,mentions=[]){
        if(!this.socket||!this.online) return;
        let attempts=0;
        while(attempts<3){
            try{
                await this.socket.sendMessage(jid,{text,...(mentions.length?{mentions}:{})});
                return;
            }catch(e){
                attempts++;
                if(isRateErr(e)){ await delay(3000); }       // rate-limit → wait and retry
                else { console.error(`[${this.id}] send err:`,e.message); return; }
            }
        }
    }
}

// ═════════════════════════════════════════════
//  HUB  — manages all sessions
// ═════════════════════════════════════════════
class Hub {
    constructor(){
        this.sessions = new Map();
        this.router   = new Router();
        this.count    = 0;
        this.disk     = readJson(PATH_NETWORK,{count:0,list:[]});
        this.count    = this.disk.count||0;
    }

    _save(){
        writeJson(PATH_NETWORK,{
            count:this.count,
            list:[...this.sessions.entries()].map(([id,s])=>({id,phone:s.phone,online:s.online}))
        });
    }

    async boot(){
        // Auto-load existing sessions from folder if not in disk
        const sessionDirs = fs.existsSync('./sessions') ? fs.readdirSync('./sessions') : [];
        for (const id of sessionDirs) {
            if (fs.statSync(`./sessions/${id}`).isDirectory() && !this.disk.list?.find(i => i.id === id)) {
                this.disk.list.push({ id, phone: null, online: false });
            }
        }

        // Ensure at least 4 seasons/slots exist
        const seasons = ['spring', 'summer', 'autumn', 'winter'];
        for (const s of seasons) {
            if (!this.disk.list?.find(i => i.id === s)) {
                this.disk.list.push({ id: s, phone: null, online: false });
            }
        }

        const saved = this.disk.list || [];
        console.log(`[HUB] Initializing ${saved.length} slots/sessions…`);

        for(const entry of saved){
            const ap=PATH_AUTH(entry.id);
            const hasFiles=fs.existsSync(ap)&&fs.readdirSync(ap).length>0;
            
            // Only init if it has files (already logged in) or it's the primary and we need to start
            if (hasFiles) {
                console.log(`[HUB] Restoring: ${entry.id}`);
                const s = new Session(entry.id, entry.phone, this, null);
                this.sessions.set(entry.id, s);
                this.router.attach(entry.id, s);
                s.init();
                await delay(1500);
            } else {
                // Register slot but don't init until .addbot is used
                const s = new Session(entry.id, entry.phone, this, null);
                this.sessions.set(entry.id, s);
                this.router.attach(entry.id, s);
            }
        }

        const primary = this.router.getPrimary();
        if (!primary && !sessionDirs.some(id => fs.readdirSync(`./sessions/${id}`).length > 0)) {
            console.log('\n[HUB] No active sessions found.');
            const ph = await question('Enter number for first bot (e.g. 919876543210) or press Enter to skip: ');
            if (ph?.trim()) {
                const c = ph.replace(/\D/g, '');
                if (c.length >= 10) await this.link(c, null);
            }
        }
        this._save();
    }

    async link(phone,notifyJid=null){
        // Try to find an empty season slot first
        const seasons = ['spring', 'summer', 'autumn', 'winter'];
        let id = null;
        for (const s of seasons) {
            const sess = this.sessions.get(s);
            if (sess && !sess.online && (!fs.existsSync(PATH_AUTH(s)) || fs.readdirSync(PATH_AUTH(s)).length === 0)) {
                id = s;
                break;
            }
        }

        if (!id) {
            this.count++;
            id = `X${this.count}`;
        }

        const s = new Session(id, phone, this, notifyJid);
        this.sessions.set(id, s);
        this.router.attach(id, s);
        await s.init();
        this._save();
        return `${TAG}\n\n⏳ ${g('session')} ${id} ${g('created for')} +${phone}\n🔑 ${g('pairing code will arrive shortly')}\n\n${g('check the next message for the code')}`;
    }

    unlink(id){
        if(this.sessions.has(id)){
            const s = this.sessions.get(id);
            if (s) {
                s.online = false;
                // session folder removal is handled in Session close event if logged out
            }
            this.router.detach(id);
            this.sessions.delete(id);
            this._save();
        }
    }
}

// ─────────────────────────────────────────────
//  START
// ─────────────────────────────────────────────
console.log(`
◈   ʙᴏᴛ  ⚡

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  commands  :  .f1–.f7  .nc  .conemo  .ncemo
               .spam  .swipe  .txt  .slide
               .voice  .voiceatk  .img
  stop all  :  .killall
  threads   :  15 per attack ⚡
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);

const hub = new Hub();
await hub.boot();
rl.close();

console.log(`\n  ✅  sasuke bot is live`);
console.log(`  →   send .admin in DM to claim owner 🔐`);
console.log(`  →   send .menu  in group to see commands ⚡\n`);
