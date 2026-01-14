import {
  makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  makeCacheableSignalKeyStore,
  isJidGroup
} from '@whiskeysockets/baileys'

//import qrcode from 'qrcode-terminal'
import pino from 'pino'
import { readFileSync, existsSync } from 'fs'
import { createInterface } from 'readline'

const logger = pino({ level: 'silent' })

let sock = null
let isReady = false
let lastQR = null
let reconnecting = false
let qrConsumed = false


async function start(sessionId = 'default') {
  try {
    const { state, saveCreds } = await useMultiFileAuthState(
      `./auth/session_${sessionId}`
    )

    const { version, isLatest } = await fetchLatestBaileysVersion()
    console.log(`BAILEYS_VERSION:${version.join('.')}_Latest:${isLatest}`)

    sock = makeWASocket({
      auth: {
        creds: state.creds,
        keys: makeCacheableSignalKeyStore(state.keys, logger)
      },
      logger,
      version,
      browser: ['Bailyeys', 'Desktop', '118.0.0'],
      printQRInTerminal: false,
      syncFullHistory: false,
      markOnlineOnConnect: true,
      generateHighQualityLinkPreview: false,
      getMessage: async () => ({ conversation: '' })
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', (update) => {
  const { connection, lastDisconnect, qr } = update

  // ---------- QR (one-time only) ----------
  if (qr && !qrConsumed) {
     qrConsumed = true
  lastQR = qr
  const qrPayload = {
  type: "qr",
  format: "raw", // future-proof
  data: qr
}

console.log("QR_DATA:" + JSON.stringify(qrPayload)) 
  }

  // ---------- CONNECTED ----------
  if (connection === 'open') {
    isReady = true
    qrConsumed = true
    reconnecting = false

    console.log('STATUS:CONNECTED')

    const info = {
      id: sock.user.id,
      name: sock.user.name || sock.user.verifiedName || 'Unknown',
      pushName: sock.user.pushName || ''
    }

    console.log(`ACCOUNT_INFO:${JSON.stringify(info)}`)
  }

  // ---------- CLOSED ----------
  if (connection === 'close') {
    isReady = false

    const statusCode = lastDisconnect?.error?.output?.statusCode
    console.log('STATUS:CLOSED', statusCode || 'UNKNOWN')

    // Normal after first QR scan
    if (statusCode === 515 && !reconnecting) {
      reconnecting = true
      console.log('RECONNECTING_AFTER_PAIRING')

      setTimeout(() => {
        start(sessionId)
      }, 1000)

      return
    }

  // ----- LOGGED OUT -----
  if (statusCode === DisconnectReason.loggedOut) {
    console.log('LOGGED_OUT')
  }
}
    })

  } catch (error) {
    console.error('FATAL_ERROR:', error)
    process.exit(1)
  }
  try {
    const { createInterface } = await import('readline')
    const { readFileSync } = await import('fs')

    // Handle incoming messages
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
  if (type !== 'notify') return

  for (const msg of messages) {
    if (!msg.message) continue

    // Ignore status / protocol noise
    if (msg.key.remoteJid === 'status@broadcast') continue

    const isGroup = isJidGroup(msg.key.remoteJid)
    const sender = isGroup
      ? msg.key.participant
      : msg.key.remoteJid

    const chatJid = msg.key.remoteJid
    const senderJid = isGroup ? msg.key.participant : chatJid

  let payload = {
  message_id: msg.key.id,
  chat_jid: chatJid,
  sender_jid: senderJid,
  chat_type: isGroup ? 'group' : 'personal',
  from_me: msg.key.fromMe,
  sender_name: msg.pushName || '',
  timestamp: msg.messageTimestamp
}

    // ---------------- TEXT / EMOJI ----------------
    const text =
      msg.message.conversation ||
      msg.message.extendedTextMessage?.text ||
      null

    if (text && text.trim()) {
      payload.type = 'text'
      payload.text = text

      console.log('NEW_MESSAGE:' + JSON.stringify(payload))
      continue
    }

    // ---------------- MEDIA ----------------
    if (msg.message.imageMessage) {
      payload.type = 'image'
      payload.caption = msg.message.imageMessage.caption || null

      console.log('NEW_MESSAGE:' + JSON.stringify(payload))
      continue
    }

    if (msg.message.videoMessage) {
      payload.type = msg.message.videoMessage.gifPlayback ? 'gif' : 'video'
      payload.caption = msg.message.videoMessage.caption || null

      console.log('NEW_MESSAGE:' + JSON.stringify(payload))
      continue
    }

    if (msg.message.audioMessage) {
      payload.type = 'audio'

      console.log('NEW_MESSAGE:' + JSON.stringify(payload))
      continue
    }

    if (msg.message.stickerMessage) {
      payload.type = 'sticker'
      payload.isAnimated = !!msg.message.stickerMessage.isAnimated

      console.log('NEW_MESSAGE:' + JSON.stringify(payload))
      continue
    }

    if (msg.message.documentMessage) {
      payload.type = 'document'
      payload.fileName = msg.message.documentMessage.fileName || null
      payload.mimeType = msg.message.documentMessage.mimetype || null

      console.log('NEW_MESSAGE:' + JSON.stringify(payload))
      continue
    }

    // Ignore everything else silently
  }
})

    // Handle presence updates
    sock.ev.on('presence.update', async (presence) => {
      // Format presence info for better readability
      const formatted = {
        id: presence.id,
        presences: presence.presences
      }
      console.log('PRESENCE_UPDATE:' + JSON.stringify(formatted))
    })

    sock.ev.on('messages.update', async (updates) => {
  for (const update of updates) {
    
    // Check if message was read
    if (update.update.status === 3) {  // Status 3 = read/seen
      console.log('MESSAGE_READ:' + JSON.stringify({
        message_id: update.key.id,
        chat_jid: update.key.remoteJid,
        participant: update.key.participant || null,
        timestamp: Date.now()
      }))
    }
  }
})

//new handler for the reaction
  sock.ev.on('messages.reaction', async (reactions) => {
  for (const reaction of reactions) {
    console.log('MESSAGE_REACTION:' + JSON.stringify({
      message_id: reaction.key.id,
      chat_jid: reaction.key.remoteJid,
      reactor_jid: reaction.key.participant || reaction.key.remoteJid,
      emoji: reaction.reaction.text,
      timestamp: reaction.reaction.senderTimestampMs,
      from_me: reaction.key.fromMe
    }))
  }
})


    // Handle group participants updates
    sock.ev.on('group-participants.update', async (update) => {
      console.log('GROUP_PARTICIPANTS_UPDATE:' + JSON.stringify(update))
    })

    // Listen for commands from Python stdin
    const rl = createInterface({
      input: process.stdin,
      terminal: false
    })

    rl.on('line', async (line) => {
      try {
        const command = JSON.parse(line)
        await handleCommand(command)
      } catch (error) {
        console.log('COMMAND_ERROR:' + JSON.stringify({ 
          error: error.message,
          line: line 
        }))
      }
    })

    // Handle process exit
    process.on('SIGINT', () => {
      console.log('PROCESS_EXIT')
      process.exit(0)
    })

    return sock
  } catch (error) {
    console.error('FATAL_ERROR:', error.message)
    process.exit(1)
  }
}

async function handleCommand(command) {
  if (!sock || !isReady) {
    sendResponse(command, false, 'Not connected or not ready')
    return
  }

  try {
    switch (command.action) {
      // ========== MESSAGING ==========
      
      case 'send_message':
        await sock.sendMessage(command.data.to, { 
          text: command.data.text 
        })
        sendResponse(command, true, 'Message sent')
        break

      case 'send_image':
        try {
          const imageBuffer = readFileSync(command.data.image)
          await sock.sendMessage(command.data.to, {
            image: imageBuffer,
            caption: command.data.caption || ''
          })
          sendResponse(command, true, 'Image sent')
        } catch (error) {
          sendResponse(command, false, `Failed to read image: ${error.message}`)
        }
        break

      case 'send_video':
        try {
          const videoBuffer = readFileSync(command.data.video)
          await sock.sendMessage(command.data.to, {
            video: videoBuffer,
            caption: command.data.caption || ''
          })
          sendResponse(command, true, 'Video sent')
        } catch (error) {
          sendResponse(command, false, `Failed to send video: ${error.message}`)
        }
        break

      case 'send_audio':
        try {
          const audioBuffer = readFileSync(command.data.audio)
          await sock.sendMessage(command.data.to, {
            audio: audioBuffer,
            mimetype: 'audio/mp4'
          })
          sendResponse(command, true, 'Audio sent')
        } catch (error) {
          sendResponse(command, false, `Failed to send audio: ${error.message}`)
        }
        break

      case 'send_document':
        try {
          const docBuffer = readFileSync(command.data.document)
          await sock.sendMessage(command.data.to, {
            document: docBuffer,
            fileName: command.data.filename,
            mimetype: getMimeType(command.data.filename)
          })
          sendResponse(command, true, 'Document sent')
        } catch (error) {
          sendResponse(command, false, `Failed to send document: ${error.message}`)
        }
        break

      // ========== USER QUERIES ==========
      
      case 'on_whatsapp':
        try {
          const [result] = await sock.onWhatsApp(command.data.jid)
          sendSyncResponse(command, {
            exists: result?.exists || false,
            jid: result?.jid || null
          })
        } catch (error) {
          sendSyncResponse(command, { exists: false, jid: null })
        }
        break

      case 'fetch_status':
        try {
          const status = await sock.fetchStatus(command.data.jid)
          sendSyncResponse(command, { status: status || '' })
        } catch (error) {
          sendSyncResponse(command, { status: '' })
        }
        break

      case 'profile_picture_url':
        try {
          const ppUrl = await sock.profilePictureUrl(
            command.data.jid, 
            command.data.type || 'preview'
          )
          sendSyncResponse(command, { url: ppUrl })
        } catch (error) {
          sendSyncResponse(command, { url: null })
        }
        break

      case 'get_business_profile':
        try {
          const profile = await sock.getBusinessProfile(command.data.jid)
          sendSyncResponse(command, profile)
        } catch (error) {
          sendSyncResponse(command, null)
        }
        break

      case 'presence_subscribe':
        await sock.presenceSubscribe(command.data.jid)
        sendResponse(command, true, 'Subscribed to presence')
        break

      case 'fetch_message_history':
        // Note: Requires oldest message - implement based on your needs
        sendResponse(command, false, 'Not implemented - requires message store')
        break

      // ========== PROFILE MANAGEMENT ==========
      
      case 'update_profile_status':
        await sock.updateProfileStatus(command.data.status)
        sendResponse(command, true, 'Profile status updated')
        break

      case 'update_profile_name':
        await sock.updateProfileName(command.data.name)
        sendResponse(command, true, 'Profile name updated')
        break

      case 'update_profile_picture':
        try {
          const imageBuffer = readFileSync(command.data.image)
          await sock.updateProfilePicture(command.data.jid, imageBuffer)
          sendResponse(command, true, 'Profile picture updated')
        } catch (error) {
          sendResponse(command, false, `Failed to update picture: ${error.message}`)
        }
        break

      case 'remove_profile_picture':
        await sock.removeProfilePicture(command.data.jid)
        sendResponse(command, true, 'Profile picture removed')
        break

      // ========== PRESENCE - 🔧 FIX 2: Proper typing indicator handling ==========
      
      case 'send_presence_update':
        try {
          // Baileys requires the JID in the second parameter
          await sock.sendPresenceUpdate(
            command.data.state,
            command.data.to
          )
          sendResponse(command, true, 'Presence updated')
        } catch (error) {
          sendResponse(command, false, `Failed to send presence: ${error.message}`)
        }
        break

      case 'typing':
        try {
          // This is a simpler wrapper, ensure proper state and JID
          await sock.sendPresenceUpdate(
            command.data.state || 'composing',
            command.data.to
          )
          sendResponse(command, true, 'Typing state sent')
        } catch (error) {
          sendResponse(command, false, `Failed to send typing: ${error.message}`)
        }
        break

      // ========== READ RECEIPTS ==========
      
      case 'read_messages':
        await sock.readMessages(command.data.keys)
        sendResponse(command, true, 'Messages marked as read')
        break

      case 'mark_read':
        await sock.readMessages([{
          remoteJid: command.data.from,
          id: command.data.id,
          participant: command.data.participant
        }])
        sendResponse(command, true, 'Marked as read')
        break

      // ========== GROUP OPERATIONS ==========
      
      case 'group_metadata':
        try {
          const metadata = await sock.groupMetadata(command.data.jid)
          sendSyncResponse(command, metadata)
        } catch (error) {
          sendSyncResponse(command, null)
        }
        break

      case 'group_create':
        try {
          const result = await sock.groupCreate(
            command.data.subject,
            command.data.participants
          )
          sendSyncResponse(command, {
            id: result.id,
            subject: command.data.subject
          })
        } catch (error) {
          sendSyncResponse(command, null)
        }
        break

      case 'group_leave':
        await sock.groupLeave(command.data.jid)
        sendResponse(command, true, 'Left group')
        break

      case 'group_update_subject':
        await sock.groupUpdateSubject(command.data.jid, command.data.subject)
        sendResponse(command, true, 'Group subject updated')
        break

      case 'group_update_description':
        await sock.groupUpdateDescription(command.data.jid, command.data.description)
        sendResponse(command, true, 'Group description updated')
        break

      case 'group_participants_update':
        await sock.groupParticipantsUpdate(
          command.data.jid,
          command.data.participants,
          command.data.action
        )
        sendResponse(command, true, `Participants ${command.data.action}ed`)
        break

      case 'group_setting_update':
        await sock.groupSettingUpdate(
          command.data.jid,
          command.data.setting
        )
        sendResponse(command, true, 'Group settings updated')
        break

      // ========== UTILITY ==========
      
      case 'get_contacts':
        const contacts = sock.store?.contacts ? Object.values(sock.store.contacts) : []
        sendSyncResponse(command, { contacts })
        break

      case 'get_chats':
        const chats = sock.store?.chats ? Object.values(sock.store.chats) : []
        sendSyncResponse(command, { chats })
        break

      default:
        sendResponse(command, false, 'Unknown command: ' + command.action)
    }
  } catch (error) {
    sendResponse(command, false, error.message)
  }
}

// Helper to send async response
function sendResponse(command, success, message) {
  const response = {
    success,
    message,
    command: command.action
  }
  
  if (command.request_id) {
    response.request_id = command.request_id
  }
  
  console.log('COMMAND_RESPONSE:' + JSON.stringify(response))
}

// Helper to send sync response (for queries)
function sendSyncResponse(command, data) {
  const response = {
    success: true,
    data,
    request_id: command.request_id
  }
  
  console.log('COMMAND_RESPONSE:' + JSON.stringify(response))
}

// Helper to determine MIME type
function getMimeType(filename) {
  const ext = filename.split('.').pop().toLowerCase()
  const mimeTypes = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'txt': 'text/plain',
    'zip': 'application/zip',
    'rar': 'application/x-rar-compressed'
  }
  return mimeTypes[ext] || 'application/octet-stream'
}

// Process starting from here
const sessionId = process.argv[2] || 'default'
start(sessionId)