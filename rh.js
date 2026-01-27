import makeWASocket, { useMultiFileAuthState, DisconnectReason, delay, fetchLatestBaileysVersion, Browsers, downloadMediaMessage, generateWAMessageFromContent, proto } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import pino from 'pino';
import fs from 'fs';
import readline from 'readline';
import gtts from 'node-gtts';

const ROLES_FILE = './data/roles.json';
const BOTS_FILE = './data/bots.json';
const DELAYS_FILE = './data/ncDelays.json';

const defaultRoles = {
    admins: [],
    subAdmins: {}
};

const defaultDelays = {
    nc1: 200,
    nc2: 200,
    nc3: 200,
    nc4: 200,
    nc5: 200,
    nc7: 200,
    nc8: 200
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
    return roles.admins.includes(jid);
}

function isSubAdmin(jid, groupJid) {
    return roles.subAdmins[groupJid]?.includes(jid) || false;
}

function hasPermission(jid, groupJid) {
    return isAdmin(jid) || isSubAdmin(jid, groupJid);
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
    const index = roles.admins.indexOf(jid);
    if (index > -1) {
        roles.admins.splice(index, 1);
        saveRoles(roles);
        return true;
    }
    return false;
}

function addSubAdmin(jid, groupJid) {
    if (!roles.subAdmins[groupJid]) {
        roles.subAdmins[groupJid] = [];
    }
    if (!roles.subAdmins[groupJid].includes(jid)) {
        roles.subAdmins[groupJid].push(jid);
        saveRoles(roles);
        return true;
    }
    return false;
}

function removeSubAdmin(jid, groupJid) {
    if (roles.subAdmins[groupJid]) {
        const index = roles.subAdmins[groupJid].indexOf(jid);
        if (index > -1) {
            roles.subAdmins[groupJid].splice(index, 1);
            saveRoles(roles);
            return true;
        }
    }
    return false;
}

const emojiArrays = {
    nc1: ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '😍', '🥰'],
    nc2: ['💋', '❤️', '🩶', '🤍', '🩷', '💘', '💝', '💝', '❤️‍🩹', '💔', '❤️‍🔥', '💓', '💗'],
    nc3: ['👍', '👎', '🫶', '🙌', '👐', '🤲', '🤜', '🤛', '✊', '👊', '🫳', '🫴', '🫱', '🫲'],
    nc4: ['💐', '🌹', '🥀', '🌺', '🌷', '🪷', '🌸', '💮', '🏵️', '🪻', '🌻', '🌼'],
    nc5: ['☀️', '🌞', '🌝', '🌚', '🌜', '🌛', '🌙', '⭐', '🌟', '✨', '🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'],
    nc7: ['🦁', '🐯', '🐱', '🐺', '🙈', '🐮', '🐷', '🦄', '🦚', '🐳', '🐋', '🐋', '🐬', '🦈'],
    nc8: ['🍓', '🍒', '🍎', '🍅', '🌶️', '🍉', '🍑', '🍊', '🥕', '🥭', '🍍', '🍌', '🌽', '🍋', '🍋‍🟩', '🍈', '🍐', '🫛', '🍆', '🍇']
};

const RahulMenu = `
╔══════════════════════════════════════╗
║  ⚡⚡⚡ Rahul BOT ⚡⚡⚡              ║
╠══════════════════════════════════════╣
║     ⚡ MULTI-BOT Rahul SYSTEM ⚡    ║
╠══════════════════════════════════════╣
║  👑 ADMIN COMMANDS                   ║
╠══════════════════════════════════════╣
║  +admin      → Become admin (DM)     ║
║  -admin      → Remove yourself       ║
║  +sub        → Make sub-admin (reply)║
║  -sub        → Remove sub-admin      ║
╠══════════════════════════════════════╣
║  🤖 BOT MANAGEMENT                   ║
╠══════════════════════════════════════╣
║  +add [num]  → Add new bot           ║
║  +bots       → List all bots         ║
║  +ping       → Check bot latency     ║
╠══════════════════════════════════════╣
║  ⚡ EMOJI NC ATTACKS ⚡               ║
╠══════════════════════════════════════╣
║  +nc1 [text] → 😀😃😄😁😆😅😂😍🥰       ║
║  +nc2 [text] → 💋❤️🩶🤍🩷💘💝          ║
║  +nc3 [text] → 👍👎🫶🙌👐🤲           ║
║  +nc4 [text] → 💐🌹🥀🌺🌷🪷           ║
║  +nc5 [text] → ☀️🌞🌝🌚🌜🌛           ║
║  +nc7 [text] → 🦁🐯🐱🐺🙈🐮           ║
║  +nc8 [text] → 🍓🍒🍎🍅🌶️🍉           ║
║                                      ║
║  +delaync1 [ms] → Set nc1 delay      ║
║  +delaync2 [ms] → Set nc2 delay      ║
║  +delaync3 [ms] → Set nc3 delay      ║
║  +delaync4 [ms] → Set nc4 delay      ║
║  +delaync5 [ms] → Set nc5 delay      ║
║  +delaync7 [ms] → Set nc7 delay      ║
║  +delaync8 [ms] → Set nc8 delay      ║
║                                      ║
║  -nc         → Stop NC attacks       ║
╠══════════════════════════════════════╣
║  💬 MESSAGE ATTACKS                  ║
╠══════════════════════════════════════╣
║  +s [text] [delay]  → Slide attack   ║
║  -s                 → Stop slides    ║
║  +txt [text] [delay]→ Text spam      ║
║  -txt               → Stop text      ║
╠══════════════════════════════════════╣
║  🎤 TTS VOICE ATTACKS                ║
╠══════════════════════════════════════╣
║  +tts [text]        → Send voice     ║
║  +ttsatk [text] [delay] → Voice spam ║
║  -ttsatk            → Stop voice     ║
╠══════════════════════════════════════╣
║  📸 PICTURE ATTACKS                  ║
╠══════════════════════════════════════╣
║  +pic [delay]       → Pic spam       ║
║                      (reply to pic)  ║
║  -pic               → Stop pic       ║
╠══════════════════════════════════════╣
║  🛑 STOP ALL                         ║
╠══════════════════════════════════════╣
║  -all        → Stop all attacks      ║
╠══════════════════════════════════════╣
║  📋 INFO                             ║
╠══════════════════════════════════════╣
║  +menu       → Show this menu        ║
║  +status     → Active attacks        ║
╠══════════════════════════════════════╣
║       ⚡ Rahul POWER ⚡             ║
╚══════════════════════════════════════╝
`;

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const question = (text) => new Promise((resolve) => rl.question(text, resolve));

async function generateTTS(text, lang = 'en') {
    return new Promise((resolve, reject) => {
        const tts = gtts(lang);
        const chunks = [];
        
        tts.stream(text).on('data', (chunk) => {
            chunks.push(chunk);
        }).on('end', () => {
            resolve(Buffer.concat(chunks));
        }).on('error', (err) => {
            reject(err);
        });
    });
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
                                    text: `🤖 *${this.botId} PAIRING CODE* 🤖\n\n` +
                                          `╔══════════════════════════════════╗\n` +
                                          `║      YOUR PAIRING CODE IS:       ║\n` +
                                          `╠══════════════════════════════════╣\n` +
                                          `║          ${code}              ║\n` +
                                          `╠══════════════════════════════════╣\n` +
                                          `║  Go to WhatsApp > Linked Devices ║\n` +
                                          `║  > Link a Device > Link with     ║\n` +
                                          `║  phone number instead            ║\n` +
                                          `╚══════════════════════════════════╝\n\n` +
                                          `📱 Number: ${this.phoneNumber}`
                                });
                            }
                        } else {
                            console.log(`\n╔══════════════════════════════════╗`);
                            console.log(`║   ${this.botId} PAIRING CODE        ║`);
                            console.log(`╠══════════════════════════════════╣`);
                            console.log(`║          ${code}              ║`);
                            console.log(`╠══════════════════════════════════╣`);
                            console.log(`║  Go to WhatsApp > Linked Devices ║`);
                            console.log(`║  > Link a Device > Link with     ║`);
                            console.log(`║  phone number instead            ║`);
                            console.log(`╚══════════════════════════════════╝\n`);
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
            const senderIsAdmin = isAdmin(sender);
            const senderIsSubAdmin = isGroup ? isSubAdmin(sender, from) : false;
            const senderHasPermission = senderIsAdmin || senderIsSubAdmin;

            if (isDM && text === '+admin') {
                if (roles.admins.length === 0) {
                    addAdmin(sender);
                    await this.sendMessage(from, `⚡ *Rahul ${this.botId}* ⚡\n\n✅ You are now the ADMIN!\n\nSend *+menu* to see commands`);
                    console.log(`[${this.botId}] New admin:`, sender);
                } else if (senderIsAdmin) {
                    await this.sendMessage(from, `⚠️ You are already the admin! - ${this.botId}`);
                } else {
                    await this.sendMessage(from, `❌ Admin already exists! Only one admin allowed. - ${this.botId}`);
                }
                return;
            }

            if (isDM && text === '-admin') {
                if (senderIsAdmin) {
                    removeAdmin(sender);
                    await this.sendMessage(from, `✅ You are no longer an admin! - ${this.botId}`);
                    console.log(`[${this.botId}] Removed admin:`, sender);
                } else {
                    await this.sendMessage(from, `⚠️ You are not an admin! - ${this.botId}`);
                }
                return;
            }

            if (isGroup && text === '+sub' && senderIsAdmin) {
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, `❌ Reply to someone to make them sub-admin! - ${this.botId}`);
                    return;
                }
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                if (addSubAdmin(targetJid, from)) {
                    await this.sendMessage(from, `✅ @${targetJid.split('@')[0]} is now a SUB-ADMIN! - ${this.botId}`, [targetJid]);
                } else {
                    await this.sendMessage(from, `⚠️ Already a sub-admin! - ${this.botId}`);
                }
                return;
            }

            if (isGroup && text === '-sub' && senderIsAdmin) {
                if (!msg.message.extendedTextMessage?.contextInfo?.participant) {
                    await this.sendMessage(from, `❌ Reply to someone to remove them as sub-admin! - ${this.botId}`);
                    return;
                }
                const targetJid = msg.message.extendedTextMessage.contextInfo.participant;
                if (removeSubAdmin(targetJid, from)) {
                    await this.sendMessage(from, `✅ @${targetJid.split('@')[0]} is no longer a sub-admin! - ${this.botId}`, [targetJid]);
                } else {
                    await this.sendMessage(from, `⚠️ Not a sub-admin! - ${this.botId}`);
                }
                return;
            }

            if (originalText.toLowerCase().startsWith('+add ') && senderIsAdmin) {
                const number = originalText.slice(5).trim().replace(/[^0-9]/g, '');
                if (number.length < 10) {
                    await this.sendMessage(from, `❌ Invalid phone number! - ${this.botId}\n\nUsage: +add [number]\nExample: +add 1234567890`);
                    return;
                }
                
                const result = await this.botManager.addBot(number, from);
                await this.sendMessage(from, result);
                return;
            }

            if (text === '+bots' && senderHasPermission) {
                const bots = this.botManager.commandBus.getAllBots();
                let msg = `🤖 *ACTIVE BOTS (${this.botId})* 🤖\n\n`;
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

            if (text === '+ping' && senderHasPermission) {
                const startTime = Date.now();
                await this.sendMessage(from, '🏓 Pinging...');
                const latency = Date.now() - startTime;
                await this.sendMessage(from, `⚡ *Rahul PING* ⚡\n\n🏓 Latency: ${latency}ms\n🤖 Bot: ${this.botId}`);
                return;
            }

            if (!senderHasPermission) return;

            if (text === '+menu') {
                await this.sendMessage(from, `${RahulMenu}\n\n📍 Responding from: ${this.botId}`);
                return;
            }

            if (text === '+status') {
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
⚡ *${this.botId} Rahul STATUS* ⚡
━━━━━━━━━━━━━━━━━━━━━
📊 *THIS CHAT (${this.botId})*
━━━━━━━━━━━━━━━━━━━━━
⚔️ NC Attacks: ${localName}
🎯 Slide Attacks: ${localSlide}
💀 Text Attacks: ${localTxt}
🎤 TTS Attacks: ${localTTS}
📸 Pic Attacks: ${localPic}
━━━━━━━━━━━━━━━━━━━━━
🌐 *ALL BOTS GLOBAL*
━━━━━━━━━━━━━━━━━━━━━
⚔️ NC Attacks: ${totalName}
🎯 Slide Attacks: ${totalSlide}
💀 Text Attacks: ${totalTxt}
🎤 TTS Attacks: ${totalTTS}
📸 Pic Attacks: ${totalPic}
━━━━━━━━━━━━━━━━━━━━━
🤖 Active Bots: ${allBots.filter(b => b.connected).length}/${allBots.length}
━━━━━━━━━━━━━━━━━━━━━`;
                
                await this.sendMessage(from, statusMsg);
                return;
            }

            if (text === '-all') {
                await this.botManager.commandBus.broadcastCommand('stop_all', { from }, this.botId);
                return;
            }

            for (const ncKey of ['nc1', 'nc2', 'nc3', 'nc4', 'nc5', 'nc7', 'nc8']) {
                if (originalText.toLowerCase().startsWith(`+delaync${ncKey.substring(2)} `)) {
                    const delayValue = parseInt(originalText.split(' ')[1]);
                    if (isNaN(delayValue) || delayValue < 50) {
                        await this.sendMessage(from, `❌ Delay must be >= 50ms - ${this.botId}`);
                        return;
                    }
                    ncDelays[ncKey] = delayValue;
                    saveDelays(ncDelays);
                    await this.sendMessage(from, `⚡ *Rahul ${this.botId}* ⚡\n\n✅ ${ncKey.toUpperCase()} delay set to ${delayValue}ms`);
                    return;
                }

                if (originalText.toLowerCase().startsWith(`+${ncKey} `)) {
                    const nameText = originalText.slice(ncKey.length + 2).trim();
                    if (!nameText) {
                        await this.sendMessage(from, `❌ Usage: +${ncKey} [text] - ${this.botId}\nExample: +${ncKey} RAID`);
                        return;
                    }

                    if (!isGroup) {
                        await this.sendMessage(from, `❌ Use this in a group! - ${this.botId}`);
                        return;
                    }

                    await this.botManager.commandBus.broadcastCommand('start_nc', { from, nameText, ncKey }, this.botId);
                    return;
                }
            }

            if (text === '-nc') {
                if (!isGroup) {
                    await this.sendMessage(from, `❌ Use this in a group! - ${this.botId}`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('stop_nc', { from }, this.botId);
                return;
            }

            if (originalText.toLowerCase().startsWith('+s ')) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage) {
                    await this.sendMessage(from, `❌ Reply to target\'s message! - ${this.botId}\nUsage: +s [text] [delay]`);
                    return;
                }

                const args = originalText.slice(3).trim().split(' ');
                if (args.length < 2) {
                    await this.sendMessage(from, `❌ Usage: +s [text] [delay] - ${this.botId}\nExample: +s Hello 1000`);
                    return;
                }

                const slideDelay = parseInt(args[args.length - 1]);
                const slideText = args.slice(0, -1).join(' ');

                if (isNaN(slideDelay) || slideDelay < 100) {
                    await this.sendMessage(from, `❌ Delay must be >= 100ms - ${this.botId}`);
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

            else if (text === '-s') {
                await this.botManager.commandBus.broadcastCommand('stop_slide', { from }, this.botId);
                return;
            }

            else if (originalText.toLowerCase().startsWith('+txt ')) {
                const args = originalText.slice(5).trim().split(' ');
                if (args.length < 2) {
                    await this.sendMessage(from, `❌ Usage: +txt [text] [delay] - ${this.botId}\nExample: +txt Hello 1000`);
                    return;
                }

                const txtDelay = parseInt(args[args.length - 1]);
                const txtText = args.slice(0, -1).join(' ');

                if (isNaN(txtDelay) || txtDelay < 100) {
                    await this.sendMessage(from, `❌ Delay must be >= 100ms - ${this.botId}`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_txt', { from, txtText, txtDelay }, this.botId);
                return;
            }

            else if (text === '-txt') {
                await this.botManager.commandBus.broadcastCommand('stop_txt', { from }, this.botId);
                return;
            }

            else if (originalText.toLowerCase().startsWith('+tts ')) {
                const ttsText = originalText.slice(5).trim();
                if (!ttsText) {
                    await this.sendMessage(from, `❌ Usage: +tts [text] - ${this.botId}\nExample: +tts Hello everyone`);
                    return;
                }

                try {
                    const audioBuffer = await generateTTS(ttsText);
                    await this.sock.sendMessage(from, {
                        audio: audioBuffer,
                        mimetype: 'audio/ogg; codecs=opus',
                        ptt: true
                    });
                } catch (err) {
                    console.error(`[${this.botId}] TTS error:`, err.message);
                    await this.sendMessage(from, `❌ TTS error - ${this.botId}`);
                }
                return;
            }

            else if (originalText.toLowerCase().startsWith('+ttsatk ')) {
                const args = originalText.slice(8).trim().split(' ');
                if (args.length < 2) {
                    await this.sendMessage(from, `❌ Usage: +ttsatk [text] [delay] - ${this.botId}\nExample: +ttsatk Hello 2000`);
                    return;
                }

                const ttsDelay = parseInt(args[args.length - 1]);
                const ttsText = args.slice(0, -1).join(' ');

                if (isNaN(ttsDelay) || ttsDelay < 1000) {
                    await this.sendMessage(from, `❌ Delay must be >= 1000ms (1s) - ${this.botId}`);
                    return;
                }

                await this.botManager.commandBus.broadcastCommand('start_tts', { from, ttsText, ttsDelay }, this.botId);
                return;
            }

            else if (text === '-ttsatk') {
                await this.botManager.commandBus.broadcastCommand('stop_tts', { from }, this.botId);
                return;
            }

            else if (originalText.toLowerCase().startsWith('+pic ')) {
                if (!msg.message.extendedTextMessage?.contextInfo?.quotedMessage?.imageMessage) {
                    await this.sendMessage(from, `❌ Reply to an image! - ${this.botId}\nUsage: +pic [delay]`);
                    return;
                }

                const picDelay = parseInt(originalText.slice(5).trim());
                if (isNaN(picDelay) || picDelay < 100) {
                    await this.sendMessage(from, `❌ Delay must be >= 100ms - ${this.botId}`);
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
                    await this.sendMessage(from, `❌ Error downloading image - ${this.botId}`);
                }
                return;
            }

            else if (text === '-pic') {
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
                        await delay(i * 200);
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
                    await this.sendMessage(from, `⚡ *Rahul ${ncKey.toUpperCase()} STARTED* ⚡\n\n💥 ${nameText}\n⏱️ Delay: ${nameDelay}ms\n🤖 Bot: ${this.botId}`);
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
                    await this.sendMessage(from, `⚡ *Rahul NC STOPPED* ⚡\n\n✅ Stopped ${stopped} threads - ${this.botId}`);
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
                    await this.sendMessage(from, `⚡ *Rahul SLIDE STARTED* ⚡\n\n💬 ${slideText}\n⏱️ Delay: ${slideDelay}ms\n🤖 Bot: ${this.botId}`);
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
                    await this.sendMessage(from, `⚡ *Rahul SLIDE STOPPED* ⚡\n\n✅ ${stopped} attack(s) - ${this.botId}`);
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
                    await this.sendMessage(from, `⚡ *Rahul TEXT ATTACK* ⚡\n\n💬 ${txtText}\n⏱️ Delay: ${txtDelay}ms\n🤖 Bot: ${this.botId}`);
                }
            }
            else if (commandType === 'stop_txt') {
                const { from } = data;
                const taskId = `${from}_txt`;
                if (this.activeTxtSenders.has(taskId)) {
                    this.activeTxtSenders.get(taskId).active = false;
                    this.activeTxtSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, `✅ Text attack stopped - ${this.botId}`);
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
                    await this.sendMessage(from, `⚡ *Rahul TTS ATTACK* ⚡\n\n🎤 ${ttsText}\n⏱️ Delay: ${ttsDelay}ms\n🤖 Bot: ${this.botId}`);
                }
            }
            else if (commandType === 'stop_tts') {
                const { from } = data;
                const taskId = `${from}_tts`;
                if (this.activeTTSSenders.has(taskId)) {
                    this.activeTTSSenders.get(taskId).active = false;
                    this.activeTTSSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, `✅ TTS attack stopped - ${this.botId}`);
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
                    await this.sendMessage(from, `⚡ *Rahul PIC ATTACK* ⚡\n\n📸 Picture spam started\n⏱️ Delay: ${picDelay}ms\n🤖 Bot: ${this.botId}`);
                }
            }
            else if (commandType === 'stop_pic') {
                const { from } = data;
                const taskId = `${from}_pic`;
                if (this.activePicSenders.has(taskId)) {
                    this.activePicSenders.get(taskId).active = false;
                    this.activePicSenders.delete(taskId);
                    if (sendConfirmation) {
                        await this.sendMessage(from, `✅ Pic attack stopped - ${this.botId}`);
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
                    await this.sendMessage(from, `🛑 *Rahul ${this.botId}* 🛑\n\n✅ Stopped ${stopped} attack(s)!`);
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
        
        return `🤖 *${botId} CREATED!* 🤖\n\n✅ Bot session created\n📱 Number: ${phoneNumber}\n\n⏳ Waiting for pairing code...\nCheck messages above for pairing instructions!`;
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

console.log('╔══════════════════════════════════╗');
console.log('║   ⚡ Rahul MULTI-BOT SYSTEM ⚡  ║');
console.log('║      Powered by Baileys v2.0     ║');
console.log('╚══════════════════════════════════╝\n');

const botManager = new BotManager();
await botManager.restoreSavedBots();
rl.close();

console.log('\n✅ Rahul Bot System Ready!');
console.log('📌 Send +admin in DM to become admin');
console.log('📌 Send +add [number] to add more bots\n');
