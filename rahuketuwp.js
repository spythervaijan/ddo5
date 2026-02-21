let targetUserJid = null;
let targetReplyText = null;
let targetLastMsg = null;


import makeWASocket, { useMultiFileAuthState, DisconnectReason, delay, fetchLatestBaileysVersion, Browsers, downloadMediaMessage, generateWAMessageFromContent, proto } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import fs from 'fs';
import readline from 'readline';
import googleTTS from 'google-tts-api';
import axios from 'axios';
import ytdl from 'ytdl-core';
import yts from 'yt-search';









const ROLES_FILE = './data/roles.json';
const BOTS_FILE = './data/bots.json';
const DELAYS_FILE = './data/ncDelays.json';
const autoReact = {
    enabled: false,
    emoji: "😭"
};

const defaultRoles = {
    Admin: null,
    admins: []
};


const defaultDelays = {
    nc1: 150,
    nc2: 150,
    nc3: 150,
    nc4: 150,
    nc5: 150,
    nc6: 150,
    nc7: 150,
    nc8: 150,
    nc9: 150,
    nc10: 150
};

function loadRoles() {
    try {
        if (fs.existsSync(ROLES_FILE)) {
            const data = fs.readFileSync(ROLES_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.log('[ROLES] Error loading roles, using defaults');
    }
    return { ...defaultRoles };
}

function saveRoles(roles) {
    try {
        if (!fs.existsSync('./data')) {
            fs.mkdirSync('./data', { recursive: true });
        }
        fs.writeFileSync(ROLES_FILE, JSON.stringify(roles, null, 2));
    } catch (err) {
        console.error('[ROLES] Error saving roles:', err.message);
    }
}

function loadDelays() {
    try {
        if (fs.existsSync(DELAYS_FILE)) {
            const data = fs.readFileSync(DELAYS_FILE, 'utf8');
            return { ...defaultDelays, ...JSON.parse(data) };
        }
    } catch (err) {
        console.log('[DELAYS] Error loading delays, using defaults');
    }
    return { ...defaultDelays };
}

function saveDelays(delays) {
    try {
        if (!fs.existsSync('./data')) {
            fs.mkdirSync('./data', { recursive: true });
        }
        fs.writeFileSync(DELAYS_FILE, JSON.stringify(delays, null, 2));
    } catch (err) {
        console.error('[DELAYS] Error saving delays:', err.message);
    }
}

let roles = loadRoles();
let ncDelays = loadDelays();

function isAdmin(jid) {
    return roles.Admin === jid;
}

function isAdmin(jid) {
    return roles.admins.includes(jid);
}

function hasPermission(jid) {
    return isAdmin(jid) || isAdmin(jid);
}

function setAdmin(jid) {
    if (!roles.Admin) {
        roles.Admin = jid;
        saveRoles(roles);
        return true;
    }
    return false;
}

function removeAdmin(jid) {
    if (roles.Admin === jid) {
        roles.Admin = null;
        saveRoles(roles);
        return true;
    }
    return false;
}

function addAdmin(jid) {
    if (!roles.admins.includes(jid)) {
        roles.admins.push(jid);
        saveRoles(roles);
        return true;
    }
    return false;
}

function removeAdmin(jid) {
    const i = roles.admins.indexOf(jid);
    if (i !== -1) {
        roles.admins.splice(i, 1);
        saveRoles(roles);
        return true;
    }
    return false;
}


const emojiArrays = {
    nc1:["🧬","⚕️","💠","🫧","🌊","⛎️","➿️","⚧️","🔆","❇️"],
  nc2:["👻","🔃","💤","🕷️","🎐","♨️","🪸","⛔️","🚺","♻️"],
  nc3:["🕸️","🌐","🪫","♑️","🔅","🚷","🈴","✖💱","〽️","©️"],
  nc4:["🧊","➰","〰️","◼️","◻️","⚕️","🎶","🎵","☣️","⚜️"],
  nc5:["❤️","💛","💚","🩵","💙","🤍","🩷","💖","💗","❤️‍🩹"],
  nc6:["🥶","🫠","🤣","🤓","🥸","😋","👰‍♂️","🫀","🧟‍♀️","😮‍💨"],
  nc7:["🥡","🧀","🥞","🧃","🍻","🍹","🥃","🫗","🥛","🧊"],
  nc8:["🈹","㊙️","🈴","🆘","㊙️","🈹","🥶","🚫","✨","❗"],
  nc9:["🇧🇬","🇧🇶","🇬🇬","🏴󠁧󠁢󠁷󠁬󠁳󠁿","🇦🇱","🏳","🇦🇨","🇰🇵","🇦🇶","🇮🇳","🇰🇷"],
  nc10:["🦍","🦧","🐕","🐈","🐈‍⬛","🐅","🐆","🫏","🐖","🦟"]
 
};

const NARUT0Menu = `
[ *SYSTEM*  : *RAHUL BOT* ]

---------------------------
:: ℂ𝕆𝕄𝔸ℕ𝔻𝕊 🕊️
---------------------------
> /menu
> /status
> /admins
> /bots
> /ping

----------------------------
:: 𝔾ℝ𝕆𝕌ℙ 𝕆ℙ𝔼ℝ𝔸𝕋𝕀𝕆ℕ𝕊 🌀
----------------------------
> /startnc1 to nc8 [text]
> /delaync1 to 8 [ms]
> /stopnc

----------------------------
:: 𝕄𝔼𝕊𝕊𝔸𝔾𝔼 𝔽𝕃𝕆𝕆𝔻 ❤️‍🔥
----------------------------
> /swipe [text] [delay]
> /stopswipe
> /spam [text] [delay]
> /stopspam
> /target
> /removetarget
----------------------------
:: 𝕍ℕ ℂ𝕄𝔻𝕊 🔱
----------------------------
> /tts [text]
> /ttsatk [text] [delay]
> /stopttsatk

----------------------------
:: 𝕄𝔼𝔻𝕀𝔸 ℂ𝕄𝔻𝕊 🛠
----------------------------
> /pic [delay] (reply)
> /stoppic

----------------------------
:: ℝ𝔼𝔸ℂ𝕋𝕀𝕆ℕ𝕊 ℂ𝕄𝔻𝕊 ⚡
----------------------------
> /react on
> /react off
> /react 

----------------------------
:: 𝔼𝕄𝔼ℝ𝔾𝔼ℕℂ𝕐 𝕊𝕋𝕆ℙ 🌜
----------------------------
> /stopall
> /leave
----------------------------
[𝕊𝕋𝔸𝕋𝕌𝕊 : 𝕒ℂ𝕋𝕀𝕍𝔼 ]
----------------------------
`;


const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = (text) => new Promise((resolve) => rl.question(text, resolve));

async function generateTTS(text) {
    try {
        const url = googleTTS.getAudioUrl(text, {
            lang:'hi',
            slow: false,
            host: 'https://translate.google.com',
        });

        const res = await axios.get(url, {
            responseType: 'arraybuffer',
            headers:{'user-Agent':'Mozilla/5.0'}
        });

        return Buffer.from(res.data);
    } catch (err) {
        console.error('[TTS ERROR]', err.message);
        throw err;
    }
}


class CommandBus {
    constructor() {
        this.botSessions = new Map();
        this.processedMessages = new Map();
        this.messageCleanupInterval = 60000;
        
        setInterval(() => {
            const now = Date.now();
            this.processedMessages.forEach((timestamp, msgId) => {
                if (now - timestamp > this.messageCleanupInterval) {
                    this.processedMessages.delete(msgId);
                }
            });
        }, this.messageCleanupInterval);
    }

    registerBot(botId, session) {
        this.botSessions.set(botId, session);
    }

    unregisterBot(botId) {
        this.botSessions.delete(botId);
    }

    shouldProcessMessage(msgId) {
        if (this.processedMessages.has(msgId)) {
            return false;
        }
        this.processedMessages.set(msgId, Date.now());
        return true;
    }

    async broadcastCommand(commandType, data, originBotId, sendConfirmation = true) {
        const bots = Array.from(this.botSessions.values()).filter(b => b.connected);
        
        for (const bot of bots) {
            try {
                const isOrigin = bot.botId === originBotId;
                await bot.executeCommand(commandType, data, isOrigin && sendConfirmation);
            } catch (err) {
                console.error(`[${bot.botId}] Command execution error:`, err.message);
            }
        }
    }

    getAllBots() {
        return Array.from(this.botSessions.values());
    }

    getConnectedBots() {
        return Array.from(this.botSessions.values()).filter(b => b.connected);
    }

    getLeaderBot() {
        const connected = this.getConnectedBots();
        return connected.length > 0 ? connected[0] : null;
    }
}

class BotSession {
    constructor(botId, phoneNumber, botManager, requestingJid = null) {
        this.botId = botId;
        this.phoneNumber = phoneNumber;
        this.botManager = botManager;
        this.requestingJid = requestingJid;
        this.sock = null;
        this.connected = false;
        this.botNumber = null;
        this.authPath = `./auth/${botId}`;
        this.pairingCodeRequested = false;
        
        this.activeNameChanges = new Map();
        this.activeSlides = new Map();
        this.activeTxtSenders = new Map();
        this.activeTTSSenders = new Map();
        this.activePicSenders = new Map();
    }

    async connect() {
        try {
            if (!fs.existsSync(this.authPath)) {
                fs.mkdirSync(this.authPath, { recursive: true });
            }

            const { state, saveCreds } = await useMultiFileAuthState(this.authPath);
            const { version } = await fetchLatestBaileysVersion();
            
            const needsPairing = !state.creds.registered;

            this.sock = makeWASocket({
                auth: state,
                logger: pino({ level: 'silent' }),
                browser: Browsers.macOS('Chrome'),
                version,
                printQRInTerminal: false,
                connectTimeoutMs: 60000,
                defaultQueryTimeoutMs: 0,
                keepAliveIntervalMs: 30000,
                emitOwnEvents: true,
                fireInitQueries: true,
                generateHighQualityLinkPreview: false,
                syncFullHistory: false,
                markOnlineOnConnect: false
            });

            this.sock.ev.on('connection.update', async (update) => {
                const { connection, lastDisconnect } = update;

                if (needsPairing && this.phoneNumber && !this.pairingCodeRequested && !state.creds.registered) {
                    this.pairingCodeRequested = true;
                    await delay(2000);
                    try {
                        const code = await this.sock.requestPairingCode(this.phoneNumber);
                        console.log(`[${this.botId}] Pairing code: ${code}`);
                        
                        if (this.requestingJid) {
                            const connectedBots = this.botManager.commandBus.getConnectedBots();
                            if (connectedBots.length > 0) {
                                const firstBot = connectedBots[0];
                                await firstBot.sock.sendMessage(this.requestingJid, {
                                    text: ` *${this.botId} PAIRING CODE* \n\n` +
                                          `      YOUR PAIRING CODE IS:       \n` +
                                          `           ${code}              \n` +
                                       
                                          ` Number: ${this.phoneNumber}`
                                });
                            }
                        } else {
                            console.log(`   ${this.botId} PAIRING CODE        `);
                            console.log(`          ${code}              `);
                            
                        }
                    } catch (err) {
                        console.error(`[${this.botId}] Error getting pairing code:`, err.message);
                        this.pairingCodeRequested = false;
                    }
                }

                if (connection === 'close') {
                    const statusCode = (lastDisconnect?.error instanceof Boom)
                        ? lastDisconnect.error.output.statusCode
                        : 500;

                    const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
                    
                    console.log(`[${this.botId}] Connection closed. Status: ${statusCode}`);
                    this.connected = false;

                    if (shouldReconnect) {
                        console.log(`[${this.botId}] Reconnecting in 5 seconds...`);
                        await delay(5000);
                        this.connect();
                    } else {
                        console.log(`[${this.botId}] Logged out.`);
                        this.botManager.removeBot(this.botId);
                    }
                } else if (connection === 'open') {
                    console.log(`[${this.botId}] ✅ CONNECTED!`);
                    this.connected = true;
                    this.botNumber = this.sock.user.id.split(':')[0] + '@s.whatsapp.net';
                    console.log(`[${this.botId}] Number:`, this.botNumber);
                }
            });

            this.sock.ev.on('creds.update', saveCreds);
            this.sock.ev.on('messages.upsert', async (m) => this.handleMessage(m));

        } catch (err) {
            console.error(`[${this.botId}] Connection error:`, err.message);
        }
    }

    async handleMessage({ messages, type }) {
        try {
            if (type !== 'notify') return;
            
            const msg = messages[0];
            if (!msg.message) return;
            if (msg.key.fromMe) return;
            
            const messageType = Object.keys(msg.message)[0];
            if (messageType === 'protocolMessage' || messageType === 'senderKeyDistributionMessage') return;

            const from = msg.key.remoteJid;
            const isGroup = from.endsWith('@g.us');
            const sender = isGroup ? msg.key.participant : from;
            
            const msgId = msg.key.id;
            const isLeader = this.botManager.commandBus.getLeaderBot()?.botId === this.botId;
            
            if (!isLeader && !this.botManager.commandBus.shouldProcessMessage(msgId)) {
                return;
            }
            
            if (isLeader) {
                if (!this.botManager.commandBus.shouldProcessMessage(msgId)) {
                    return;
                }
            }
            
            this.activeSlides.forEach((task, taskId) => {
                if (task.active && task.groupJid === from && task.targetJid === sender) {
                    task.latestMsg = msg;
                    task.hasNewMsg = true;
                }
            });
            
            let text = msg.message.conversation || 
                      msg.message.extendedTextMessage?.text || 
                      msg.message.imageMessage?.caption || '';

            const originalText = text;
            text = text.trim().toLowerCase();

            console.log(`[${this.botId}] MSG from ${sender}: ${text}`);

            const isDM = !isGroup;
            const senderHasPermission = hasPermission(sender);


            // SET Admin (DM ONLY)
if (isDM && text === '+Admin') {
    if (!roles.Admin) {
        setAdmin(sender);
        await this.sendMessage(from, `👑 You are now Admin`);
    } else if (isAdmin(sender)) {
        await this.sendMessage(from, `⚠️ You are already Admin`);
    } else {
        await this.sendMessage(from, `❌ Admin already exists`);
    }
    return;
}

            // Admin SELF REMOVE (DM ONLY)
if (isDM && text === '-Admin' && isAdmin(sender)) {
    removeAdmin(sender);
    await this.sendMessage(
        from,
        `❌ You are no longer Admin\n\n⚠️ Bot has no Admin now.\nUse +Admin to set new Admin`
    );
    return;
}


            // Admin GIVE ADMIN (GROUP ONLY)
if (isGroup && text === '/makeadmin' && isAdmin(sender)) {
    if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
        await this.sendMessage(from, `❌ Reply to user to make ADMIN`);
        return;
    }

    const target = msg.message.extendedTextMessage.contextInfo.participant;

    if (addAdmin(target)) {
        await this.sendMessage(
            from,
            `✅ @${target.split('@')[0]} is now ADMIN`,
            [target]
        );
    } else {
        await this.sendMessage(from, `⚠️ Already ADMIN`);
    }
    return;
}


            // Admin REMOVE ADMIN (GROUP ONLY)
if (isGroup && text === '/removeadmin' && isAdmin(sender)) {
    if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
        await this.sendMessage(from, `❌ Reply to admin to remove`);
        return;
    }

    const target = msg.message.extendedTextMessage.contextInfo.participant;

    if (removeAdmin(target)) {
        await this.sendMessage(
            from,
            `❌ @${target.split('@')[0]} removed from ADMIN`,
            [target]
        );
    } else {
        await this.sendMessage(from, `⚠️ Not an ADMIN`);
    }
    return;
}

// ADMIN LIST
if (text === '/admins' && senderHasPermission) {
    let msg = `👑 *ADMIN LIST*\n\n`;

    msg += `👑 Admin:\n`;
    msg += roles.Admin
        ? `• ${roles.Admin.split('@')[0]}\n\n`
        : `• Not set\n\n`;

    if (roles.admins.length > 0) {
        msg += `🛡 ADMINS (${roles.admins.length}):\n`;
        roles.admins.forEach((jid, i) => {
            msg += `${i + 1}. ${jid.split('@')[0]}\n`;
        });
    } else {
        msg += `🛡 ADMINS:\n• No admins`;
    }

    await this.sendMessage(from, msg);
    return;
}


            if (originalText.toLowerCase().startsWith('+add ')) {

    // 🔒 Admin CHECK
    if (!isAdmin(sender)) {
        await this.sendMessage(from, `❌ Only Admin can add new bots`);
        return;
    }

    const number = originalText
        .slice(5)
        .trim()
        .replace(/[^0-9]/g, '');

    if (number.length < 10) {
        await this.sendMessage(
            from,
            `❌ Invalid phone number!\n\nUsage: +add [number]\nExample: +add 919876543210`
        );
        return;
    }

    const result = await this.botManager.addBot(number, from);
    await this.sendMessage(from, result);
    return;
}

// 🎯 TARGET AUTO REPLY
if (
    targetUserJid &&
    msg.key.participant === targetUserJid &&
    !msg.key.fromMe
) {
    await this.sendMessage(from, targetReplyText);
}


            if (text === '/bots' && senderHasPermission) {
                const bots = this.botManager.commandBus.getAllBots();
                let msg = ` *ACTIVE BOTS (${this.botId})* \n\n`;
                msg += `Total Bots: ${bots.length}\n\n`;
                
                bots.forEach(bot => {
                    const status = bot.connected ? '✅ Online' : '⚠️ Offline';
                    msg += `${bot.botId}: ${status}\n`;
                    if (bot.botNumber) {
                        msg += `  📱 ${bot.botNumber.split('@')[0]}\n`;
                    }
                });
                
                await this.sendMessage(from, msg);
                return;
            }

            if (text === '/ping' && senderHasPermission) {
                const startTime = Date.now();
                await this.sendMessage(from, ' Pinging...');
                const latency = Date.now() - startTime;
                await this.sendMessage(from, ` *PING* \n\n Latency: ${latency}ms`);
                return;
            }

            if (!senderHasPermission) return;

            if (text === '/menu') {
                await this.sendMessage(from, `${NARUT0Menu}\n\n SEND COMMANDS TO START`);
                return;
            }

// AUTO REACT ON
if (text === '/react on' && senderHasPermission) {
    autoReact.enabled = true;
    await this.sendMessage(from, `✅ Auto React ENABLED`);
    return;
}

// AUTO REACT OFF
if (text === '/react off' && senderHasPermission) {
    autoReact.enabled = false;
    await this.sendMessage(from, `❌ Auto React DISABLED`);
    return;
}

// CHANGE REACT EMOJI
if (text.startsWith('/react ') && senderHasPermission) {
    const parts = originalText.split(' ');
    if (parts[1]) {
        autoReact.emoji = parts[1];
        await this.sendMessage(from, `✅ React emoji set to ${autoReact.emoji}`);
    }
    return;
}

// AUTO REACT TO MESSAGES
if (
    autoReact.enabled &&
    isGroup &&
    !msg.key.fromMe 
) {
    try {
        await this.sock.sendMessage(from, {
            react: {
                text: autoReact.emoji,
                key: msg.key
            }
        });
    } catch (e) {
        console.log('[AUTO REACT ERROR]', e.message);
    }
}


            if (text === '/status') {
                const allBots = this.botManager.commandBus.getAllBots();
                let totalName = 0, totalSlide = 0, totalTxt = 0, totalTTS = 0, totalPic = 0;
                
                allBots.forEach(bot => {
                    totalName += bot.activeNameChanges.size;
                    totalSlide += bot.activeSlides.size;
                    totalTxt += bot.activeTxtSenders.size;
                    totalTTS += bot.activeTTSSenders.size;
                    totalPic += bot.activePicSenders.size;
                });
                
                let localName = 0, localSlide = 0, localTxt = 0, localTTS = 0, localPic = 0;
                
                this.activeNameChanges.forEach((val, key) => {
                    if (key.startsWith(from)) localName++;
                });
                this.activeSlides.forEach((task) => {
                    if (task.groupJid === from && task.active) localSlide++;
                });
                this.activeTxtSenders.forEach((task, key) => {
                    if (key.startsWith(from) && task.active) localTxt++;
                });
                this.activeTTSSenders.forEach((task, key) => {
                    if (key.startsWith(from) && task.active) localTTS++;
                });
                this.activePicSenders.forEach((task, key) => {
                    if (key.startsWith(from) && task.active) localPic++;
                });
                
                const statusMsg = `
╭────────────────────────────╮
│     *BOT* :: *STATUS*      │
╰────────────────────────────╯

▌ *CORE STATUS*
  ├─ BOT ID      : ${this.botId}
  ├─ CONNECTION  : ${this.connected ? 'ONLINE  []' : 'OFFLINE [✘]'}

▌ *ACCESS LEVEL*
  ├─ Admin       : ${roles.Admin ? roles.Admin.split('@')[0] : 'NULL'}
  ├─ ADMINS      : ${roles.admins.length}

▌ *ATTACK MATRIX* (THIS GC)
  ├─ NC          : ${localName}
  ├─ SLIDE       : ${localSlide}
  ├─ TEXT        : ${localTxt}
  ├─ TTS         : ${localTTS}
  ├─ PIC         : ${localPic}

▌ *ATTACK MATRIX* (OTHER GC)
  ├─ NC          : ${totalName}
  ├─ SLIDE       : ${totalSlide}
  ├─ TEXT        : ${totalTxt}
  ├─ TTS         : ${totalTTS}
  ├─ PIC         : ${totalPic}

▌ *NETWORK STATUS*
  ├─ BOTS ONLINE : ${allBots.filter(b => b.connected).length}/${allBots.length}

╰────────────────────────────╯
`;

                
                await this.sendMessage(from, statusMsg);
                return;
            }

            if (text === '/stopall') {
                await this.botManager.commandBus.broadcastCommand('stop_all', { from }, this.botId);
                return;
            }

            for (const ncKey of ['nc1', 'nc2', 'nc3', 'nc4', 'nc5', 'nc6', 'nc7', 'nc8']) {
                if (originalText.toLowerCase().startsWith(`/delaync${ncKey.substring(2)} `)) {
                    const delayValue = parseInt(originalText.split(' ')[1]);
                    if (isNaN(delayValue) || delayValue < 50) {
                        await this.sendMessage(from, `❌ Delay must be >= 50ms `);
                        return;
                    }
                    ncDelays[ncKey] = delayValue;
                    saveDelays(ncDelays);
                    await this.sendMessage(from, ` ✅ ${ncKey.toUpperCase()} delay set to ${delayValue}ms`);
                    return;
                }

                if (originalText.toLowerCase().startsWith(`/start${ncKey} `)) {

    const nameText = originalText.replace(
        new RegExp(`^/start${ncKey}\\s*`, 'i'),
        ''
    ).trim();

    if (!nameText) {
        await this.sendMessage(
            from,
            `✖ Usage: /start${ncKey} [text]\nExample: /start${ncKey} RAID`
        );
        return;
    }

    if (!isGroup) {
        await this.sendMessage(from, '✖ Use this in a group');
        return;
    }

    await this.botManager.commandBus.broadcastCommand(
        'start_nc',
        { from, nameText, ncKey },
        this.botId
    );
    return;
}

            }

            if (text === '/stopnc') {
                if (!isGroup) {
                    await this.sendMessage(from, `❌ Use this in a group! `);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('stop_nc', { from }, this.botId);
                return;
            }

            if (originalText.toLowerCase().startsWith('/swipe ')) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage) {
                    await this.sendMessage(from, `❌ Reply to target\'s message! \nUsage: /swipe [text] [delay]`);
                    return;
                }

                const args = originalText
    .replace(/^\/swipe\s+/i, '')
    .trim()
    .split(' ');


                if (args.length < 2) {
                    await this.sendMessage(from, `❌ Usage: /swipe [text] [delay] \nExample: /swipe Hello 1000`);
                    return;
                }

                const slideDelay = parseInt(args[args.length - 1]);
                const slideText = args.slice(0, -1).join(' ');

                if (isNaN(slideDelay) || slideDelay < 1000) {
                    await this.sendMessage(from, `❌ Delay must be >= 1000ms `);
                    return;
                }

                const quotedParticipant = msg.message.extendedTextMessage.contextInfo.participant || 
                                        msg.message.extendedTextMessage.contextInfo.remoteJid;
                const quotedMsgId = msg.message.extendedTextMessage.contextInfo.stanzaId;
                const quotedMessage = msg.message.extendedTextMessage.contextInfo.quotedMessage;

                await this.botManager.commandBus.broadcastCommand('start_slide', {
                    from,
                    slideText,
                    slideDelay,
                    quotedParticipant,
                    quotedMsgId,
                    quotedMessage
                }, this.botId);
                return;
            }


// 🎯 TARGET AUTO REPLY (SWIPE)
if (
    targetUserJid &&
    msg.key.participant === targetUserJid &&
    msg.key.id !== targetLastMsg
) {
    targetLastMsg = msg.key.id;

    await this.sock.sendMessage(
        msg.key.remoteJid,
        { text: targetReplyText },
        { quoted: targetLastMsg } // ✅ SWIPE REPLY
    );
}

            else if (text === '/stopswipe') {
                await this.botManager.commandBus.broadcastCommand('stop_slide', { from }, this.botId);
                return;
            }

            else if (originalText.toLowerCase().startsWith('/spam ')) {
                const args = originalText.slice(5).trim().split(' ');
                if (args.length < 2) {
                    await this.sendMessage(from, `❌ Usage: /spam [text] [delay] \nExample: /spam Hello 1000`);
                    return;
                }

                const txtDelay = parseInt(args[args.length - 1]);
                const txtText = args.slice(0, -1).join(' ');

                if (isNaN(txtDelay) || txtDelay < 100) {
                    await this.sendMessage(from, `❌ Delay must be >= 100ms `);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_txt', { from, txtText, txtDelay }, this.botId);
                return;
            }





            else if (text === '/stopspam') {
                await this.botManager.commandBus.broadcastCommand('stop_txt', { from }, this.botId);
                return;
            }

            else if (originalText.toLowerCase().startsWith('/tts ')) {
                const ttsText = originalText.slice(5).trim();
                if (!ttsText) {
                    await this.sendMessage(from, `❌ Usage: /tts [text] \nExample: /tts hi`);
                    return;
                }

                try {
                    const audioBuffer = await generateTTS(ttsText);

                    await this.sock.sendMessage(from, {
                    audio: audioBuffer,
                    mimetype: 'audio/mpeg',
                  });

                } catch (err) {
                    console.error(`TTS error:`, err.message);
                    await this.sendMessage(from, `❌ TTS error `);
                }
                return;
            }

            else if (originalText.toLowerCase().startsWith('/ttsatk ')) {
                const args = originalText.slice(8).trim().split(' ');
                if (args.length < 2) {
                    await this.sendMessage(from, `❌ Usage: /ttsatk [text] [delay] \nExample: /ttsatk Hello 2000`);
                    return;
                }

                const ttsDelay = parseInt(args[args.length - 1]);
                const ttsText = args.slice(0, -1).join(' ');

                if (isNaN(ttsDelay) || ttsDelay < 1000) {
                    await this.sendMessage(from, `❌ Delay must be >= 1000ms (1s) `);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_tts', { from, ttsText, ttsDelay }, this.botId);
                return;
            }

            else if (text === '/stopttsatk') {
                await this.botManager.commandBus.broadcastCommand('stop_tts', { from }, this.botId);
                return;
            }
              

else if (originalText.toLowerCase().startsWith('/target ')) {

    if (!msg.message.extendedTextMessage?.contextInfo?.mentionedJid?.length) {
        await this.sendMessage(
            from,
            '❌ Usage: /target @user reply text'
        );
        return;
    }

    targetUserJid = msg.message.extendedTextMessage.contextInfo.mentionedJid[0];
    targetReplyText = originalText
        .replace(/^\/target\s+/i, '')
        .replace(/@\S+\s*/i, '')
        .trim();

    if (!targetReplyText) {
        await this.sendMessage(from, '❌ Reply text missing');
        return;
    }


    await this.sendMessage(
        from,
        `🎯 Target set\nUser: @${targetUserJid.split('@')[0]}`,
        { mentions: [targetUserJid] }
    );
    return;
}


else if (originalText === '/removetarget') {
    targetUserJid = null;
    targetReplyText = null;
    targetLastMsg = nulk;
    await this.sendMessage(from, '*TARGET REMOVED*');
    return;
}


else if (originalText.toLowerCase() === '/leave') {

    // Sirf group me allow
    if (!isGroup) {
        await this.sendMessage(from, '❌ Ye command sirf group me use hoti hai');
        return;
    }

    // Optional: sirf Admin/Admin allow
    if (!isAdmin && !isAdmin) {
        await this.sendMessage(from, '❌ Sirf Admin ya Admin bot ko leave kara sakta hai');
        return;
    }

    await this.sendMessage(from, '👋 Bye !! groupe leave kar raha...');

    // Bot leave group
    await this.sock.groupLeave(from);

    return;
}

// ⚡ INSTANT KICK ALL (NO DELAY)
if (text === '/kickall') {

    if (!isGroup) {
        await this.sendMessage(from, '❌ Ye command sirf group me use hoti hai');
        return;
    }

    if (!hasPermission(sender)) {
        await this.sendMessage(from, '❌ Sirf Admin ya Admin use kar sakta hai');
        return;
    }

    try {
        const meta = await this.sock.groupMetadata(from);

        // Non-admins + not bot
        const targets = meta.participants
            .filter(p => !p.admin && p.id !== this.botNumber)
            .map(p => p.id);

        if (targets.length === 0) {
            await this.sendMessage(from, '⚠️ Kick ke liye koi member nahi mila');
            return;
        }

        await this.sendMessage(from, `⚡ Instant kick started (${targets.length})`);

        // 🔥 INSTANT / PARALLEL REMOVE
        await this.sock.groupParticipantsUpdate(from, targets, 'remove');

        await this.sendMessage(from, `✅ *KICK ALL DONE*\n👢 Kicked: ${targets.length}\n🛡️ Admins skipped`);

    } catch (err) {
        console.error('InstantKick Error:', err.message);
        await this.sendMessage(from, '❌ Instant kick failed');
    }

    return;
}

            else if (originalText.toLowerCase().startsWith('/pic ')) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage) {
                    await this.sendMessage(from, `❌ Reply to an image! \nUsage: /pic [delay]`);
                    return;
                }

                const picDelay = parseInt(originalText.slice(5).trim());
                if (isNaN(picDelay) || picDelay < 100) {
                    await this.sendMessage(from, `❌ Delay must be >= 100ms `);
                    return;
                }

                const quotedMsg = {
                    key: {
                        remoteJid: from,
                        fromMe: false,
                        id: msg.message.extendedTextMessage.contextInfo.stanzaId,
                        participant: msg.message.extendedTextMessage.contextInfo.participant
                    },
                    message: msg.message.extendedTextMessage.contextInfo.quotedMessage
                };

                try {
                    const imageBuffer = await downloadMediaMessage(quotedMsg, 'buffer', {});
                    const imageMessage = msg.message.extendedTextMessage.contextInfo.quotedMessage.imageMessage;
                    
                    await this.botManager.commandBus.broadcastCommand('start_pic', { 
                        from, 
                        picDelay, 
                        imageBuffer: imageBuffer.toString('base64'),
                        mimetype: imageMessage.mimetype || 'image/jpeg'
                    }, this.botId);
                } catch (err) {
                    console.error(`[${this.botId}] Error downloading image:`, err.message);
                    await this.sendMessage(from, `❌ Error downloading image `);
                }
                return;
            }

            else if (text === '/stoppic') {
                await this.botManager.commandBus.broadcastCommand('stop_pic', { from }, this.botId);
                return;
            }

        } catch (err) {
            console.error(`[${this.botId}] ERROR:`, err);
        }
    }

    async executeCommand(commandType, data, sendConfirmation = true) {
        try {
            if (commandType === 'start_nc') {
                const { from, nameText, ncKey } = data;
                const emojis = emojiArrays[ncKey];
                const nameDelay = ncDelays[ncKey];
                
                for (let i = 0; i < 5; i++) {
                    const taskId = `${from}_${ncKey}_${i}`;
                    if (this.activeNameChanges.has(taskId)) {
                        this.activeNameChanges.delete(taskId);
                        await delay(100);
                    }

                    let emojiIndex = i * Math.floor(emojis.length / 5);
                    
                    const runLoop = async () => {
                        this.activeNameChanges.set(taskId, true);
                        await delay(i * 50);
                        while (this.activeNameChanges.get(taskId)) {
                            try {
                                const emoji = emojis[Math.floor(emojiIndex) % emojis.length];
                                const newName = `${nameText} ${emoji}`;
                                await this.sock.groupUpdateSubject(from, newName);
                                emojiIndex++;
                                await delay(nameDelay);
                            } catch (err) {
                                if (err.message?.includes('rate-overlimit')) {
                                    await delay(3000);
                                } else {
                                    await delay(nameDelay);
                                }
                            }
                        }
                    };

                    runLoop();
                }

                if (sendConfirmation) {
                    await this.sendMessage(from, `  *${ncKey.toUpperCase()} STARTING* \n Delay: ${nameDelay}ms`);
                }
            }
            else if (commandType === 'stop_nc') {
                const { from } = data;
                let stopped = 0;
                
                this.activeNameChanges.forEach((value, taskId) => {
                    if (taskId.startsWith(from)) {
                        this.activeNameChanges.set(taskId, false);
                        this.activeNameChanges.delete(taskId);
                        stopped++;
                    }
                });

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, ` *NC STOPPED* `);
                }
            }
            else if (commandType === 'start_slide') {
                const { from, slideText, slideDelay, quotedParticipant, quotedMsgId, quotedMessage } = data;
                
                const taskId = `${from}_${quotedParticipant}`;
                
                if (this.activeSlides.has(taskId)) {
                    this.activeSlides.get(taskId).active = false;
                    await delay(200);
                }

                const slideTask = {
                    targetJid: quotedParticipant,
                    text: slideText,
                    groupJid: from,
                    latestMsg: {
                        key: {
                            remoteJid: from,
                            fromMe: false,
                            id: quotedMsgId,
                            participant: quotedParticipant
                        },
                        message: quotedMessage
                    },
                    hasNewMsg: true,
                    lastRepliedId: null,
                    active: true
                };

                this.activeSlides.set(taskId, slideTask);

                const runSlide = async () => {
                    while (slideTask.active) {
                        try {
                            await this.sock.sendMessage(from, { 
                                text: slideText 
                            }, { 
                                quoted: slideTask.latestMsg
                            });
                        } catch (err) {
                            console.error(`[${this.botId}] SLIDE Error:`, err.message);
                        }
                        await delay(slideDelay);
                    }
                };

                runSlide();

                if (sendConfirmation) {
                    await this.sendMessage(from, ` *SLIDE STARTING* \n\n ${slideText}\n Delay: ${slideDelay}ms`);
                }
            }
            else if (commandType === 'stop_slide') {
                const { from } = data;
                let stopped = 0;
                this.activeSlides.forEach((task, taskId) => {
                    if (task.groupJid === from) {
                        task.active = false;
                        this.activeSlides.delete(taskId);
                        stopped++;
                    }
                });

                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, ` *SLIDE STOPPED* `);
                }
            }
            else if (commandType === 'start_txt') {
                const { from, txtText, txtDelay } = data;
                
                const taskId = `${from}_txt`;
                
                if (this.activeTxtSenders.has(taskId)) {
                    this.activeTxtSenders.get(taskId).active = false;
                    await delay(200);
                }

                const txtTask = { active: true };
                this.activeTxtSenders.set(taskId, txtTask);

                const runTxt = async () => {
                    while (txtTask.active) {
                        try {
                            await this.sock.sendMessage(from, { text: txtText });
                        } catch (err) {
                            console.error(`[${this.botId}] TXT Error:`, err.message);
                        }
                        await delay(txtDelay);
                    }
                };

                runTxt();

                if (sendConfirmation) {
                    await this.sendMessage(from, ` *SPAM ATTACK* \n\n⏱️ Delay: ${txtDelay}ms`);
                }
            }
            else if (commandType === 'stop_txt') {
                const { from } = data;
                const taskId = `${from}_txt`;
                if (this.activeTxtSenders.has(taskId)) {
                    this.activeTxtSenders.get(taskId).active = false;
                    this.activeTxtSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, `✅ SPAM stopped `);
                    }
                }
            }
            else if (commandType === 'start_tts') {
                const { from, ttsText, ttsDelay } = data;
                
                const taskId = `${from}_tts`;
                
                if (this.activeTTSSenders.has(taskId)) {
                    this.activeTTSSenders.get(taskId).active = false;
                    await delay(200);
                }

                const ttsTask = { active: true };
                this.activeTTSSenders.set(taskId, ttsTask);

                const runTTS = async () => {
                    while (ttsTask.active) {
                        try {
                            const audioBuffer = await generateTTS(ttsText);
                            await this.sock.sendMessage(from, {
                                audio: audioBuffer,
                                mimetype: 'audio/ogg; codecs=opus',
                                ptt: true
                            });
                        } catch (err) {
                            console.error(`[${this.botId}] TTS Error:`, err.message);
                        }
                        await delay(ttsDelay);
                    }
                };

                runTTS();

                if (sendConfirmation) {
                    await this.sendMessage(from, ` *TTS ATTACK* `);
                }
            }
            else if (commandType === 'stop_tts') {
                const { from } = data;
                const taskId = `${from}_tts`;
                if (this.activeTTSSenders.has(taskId)) {
                    this.activeTTSSenders.get(taskId).active = false;
                    this.activeTTSSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, `✅ TTS stopped `);
                    }
                }
            }
            else if (commandType === 'start_pic') {
                const { from, picDelay, imageBuffer, mimetype } = data;
                
                const taskId = `${from}_pic`;
                
                if (this.activePicSenders.has(taskId)) {
                    this.activePicSenders.get(taskId).active = false;
                    await delay(200);
                }

                const picTask = { active: true, buffer: Buffer.from(imageBuffer, 'base64'), mimetype };
                this.activePicSenders.set(taskId, picTask);

                const runPic = async () => {
                    while (picTask.active) {
                        try {
                            await this.sock.sendMessage(from, {
                                image: picTask.buffer,
                                mimetype: picTask.mimetype
                            });
                        } catch (err) {
                            console.error(`[${this.botId}] PIC Error:`, err.message);
                        }
                        await delay(picDelay);
                    }
                };

                runPic();

                if (sendConfirmation) {
                    await this.sendMessage(from, ` *PIC SPAM* \n\n⏱️ Delay: ${picDelay}ms`);
                }
            }
            else if (commandType === 'stop_pic') {
                const { from } = data;
                const taskId = `${from}_pic`;
                if (this.activePicSenders.has(taskId)) {
                    this.activePicSenders.get(taskId).active = false;
                    this.activePicSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, `✅ Pic SPAM stopped `);
                    }
                }
            }
            else if (commandType === 'stop_all') {
                const { from } = data;
                let stopped = 0;
                
                this.activeNameChanges.forEach((value, taskId) => {
                    if (taskId.startsWith(from)) {
                        this.activeNameChanges.set(taskId, false);
                        this.activeNameChanges.delete(taskId);
                        stopped++;
                    }
                });
                
                this.activeSlides.forEach((task, taskId) => {
                    if (task.groupJid === from) {
                        task.active = false;
                        this.activeSlides.delete(taskId);
                        stopped++;
                    }
                });
                
                const txtTaskId = `${from}_txt`;
                if (this.activeTxtSenders.has(txtTaskId)) {
                    this.activeTxtSenders.get(txtTaskId).active = false;
                    this.activeTxtSenders.delete(txtTaskId);
                    stopped++;
                }

                const ttsTaskId = `${from}_tts`;
                if (this.activeTTSSenders.has(ttsTaskId)) {
                    this.activeTTSSenders.get(ttsTaskId).active = false;
                    this.activeTTSSenders.delete(ttsTaskId);
                    stopped++;
                }

                const picTaskId = `${from}_pic`;
                if (this.activePicSenders.has(picTaskId)) {
                    this.activePicSenders.get(picTaskId).active = false;
                    this.activePicSenders.delete(picTaskId);
                    stopped++;
                }
                
                if (stopped > 0 && sendConfirmation) {
                    await this.sendMessage(from, ` ✅ Stopped `);
                }
            }
        } catch (err) {
            console.error(`[${this.botId}] executeCommand error:`, err.message);
        }
    }

    async sendMessage(jid, text, mentions = []) {
        if (!this.sock || !this.connected) return;
        try {
            const message = { text };
            if (mentions.length > 0) {
                message.mentions = mentions;
            }
            await this.sock.sendMessage(jid, message);
        } catch (err) {
            console.error(`[${this.botId}] Send message error:`, err.message);
        }
    }
}

class BotManager {
    constructor() {
        this.bots = new Map();
        this.commandBus = new CommandBus();
        this.botCounter = 0;
        this.loadedData = this.loadBots();
    }

    loadBots() {
        try {
            if (fs.existsSync(BOTS_FILE)) {
                const data = fs.readFileSync(BOTS_FILE, 'utf8');
                const savedBots = JSON.parse(data);
                this.botCounter = savedBots.counter || 0;
                console.log(`[MANAGER] Found ${savedBots.bots?.length || 0} saved bot(s)`);
                return savedBots;
            }
        } catch (err) {
            console.log('[MANAGER] No saved bots found, starting fresh');
        }
        return { counter: 0, bots: [] };
    }

    saveBots() {
        try {
            if (!fs.existsSync('./data')) {
                fs.mkdirSync('./data', { recursive: true });
            }
            const data = {
                counter: this.botCounter,
                bots: Array.from(this.bots.entries()).map(([id, bot]) => ({
                    id,
                    phoneNumber: bot.phoneNumber,
                    connected: bot.connected
                }))
            };
            fs.writeFileSync(BOTS_FILE, JSON.stringify(data, null, 2));
        } catch (err) {
            console.error('[MANAGER] Error saving bots:', err.message);
        }
    }

    async restoreSavedBots() {
        if (this.loadedData.bots && this.loadedData.bots.length > 0) {
            console.log(`[MANAGER] Restoring ${this.loadedData.bots.length} bot session(s)...`);
            
            for (const botData of this.loadedData.bots) {
                const authPath = `./auth/${botData.id}`;
                const hasAuth = fs.existsSync(authPath) && fs.readdirSync(authPath).length > 0;
                
                let phoneNumber = botData.phoneNumber;
                
                if (!hasAuth && !phoneNumber) {
                    console.log(`\n[MANAGER] ${botData.id} has no credentials and no phone number.`);
                    phoneNumber = await question(`Enter phone number for ${botData.id} (e.g. 919876543210): `);
                    phoneNumber = phoneNumber.replace(/[^0-9]/g, '');
                    
                    if (!phoneNumber || phoneNumber.length < 10) {
                        console.log(`[MANAGER] Invalid number. Removing ${botData.id}...`);
                        continue;
                    }
                }
                
                const session = new BotSession(botData.id, phoneNumber, this, null);
                this.bots.set(botData.id, session);
                this.commandBus.registerBot(botData.id, session);
                
                console.log(`[MANAGER] Reconnecting ${botData.id}...`);
                await session.connect();
                await delay(2000);
            }
            
            this.saveBots();
        } else {
            console.log('[MANAGER] No saved sessions. Waiting for first bot via +add command...');
            console.log('[MANAGER] Or pair the first bot manually...\n');
            
            const phoneNumber = await question('Enter phone number for BOT1 (or press Enter to skip): ');
            if (phoneNumber && phoneNumber.trim()) {
                const cleanNumber = phoneNumber.replace(/[^0-9]/g, '');
                if (cleanNumber.length >= 10) {
                    await this.addBot(cleanNumber, null);
                }
            } else {
                console.log('[MANAGER] Skipped. Use +add command in WhatsApp to add bots.\n');
            }
        }
    }

    async addBot(phoneNumber, requestingJid = null) {
        this.botCounter++;
        const botId = `BOT${this.botCounter}`;
        
        const session = new BotSession(botId, phoneNumber, this, requestingJid);
        this.bots.set(botId, session);
        this.commandBus.registerBot(botId, session);
        
        await session.connect();
        this.saveBots();
        
        return ` *${botId} CREATED!* \n\n✅ Bot session created\n📱 Number: ${phoneNumber}`;
    }

    removeBot(botId) {
        if (this.bots.has(botId)) {
            this.commandBus.unregisterBot(botId);
            this.bots.delete(botId);
            this.saveBots();
            console.log(`[MANAGER] Removed ${botId}`);
        }
    }
}


console.log('║    RAHUL BOT CONSOLE     ║');


const botManager = new BotManager();
await botManager.restoreSavedBots();
rl.close();

console.log('\n✅ RAHUL Bot Console Ready!');
console.log('Send +Admin in DM to become Admin');
