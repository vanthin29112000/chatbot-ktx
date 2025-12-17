import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

const API_URL = '/api/chat'
// Backend API URL - có thể override bằng environment variable
const BACKEND_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Payload mặc định - sẽ dùng nếu không capture được tự động
const DEFAULT_PAYLOAD_TEMPLATE = {
  "id": "cmj8e583h11dx5l0nr92tluk6",
  "blockId": "cmgstldjf006hutqk4mroyx4o",
  "params": {
    "params": {
      "projectSlug": "trungtamquanlykytucxadhquocgiahcm",
      "pageId": "cmgstldib006futqk8rv7ro4u",
      "chatbotId": "cmgstldjf006hutqk4mroyx4o"
    }
  },
  "stream": true,
  "chatbotSessionId": "cmj8e583h11dx5l0nr92tluk6",
  "predictionId": "f9918549-15d0-46d2-9979-183206cbaff8",
  "useLegacyStreamFormat": true,
  "message": {
    "content": "",
    "role": "user"
  },
  "mode": "public"
}

function App() {
  const [messages, setMessages] = useState([
    { id: Date.now(), content: 'Xin chào! Tôi là chatbot. Bạn cần hỗ trợ gì?', isUser: false }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [payloadTemplate, setPayloadTemplate] = useState(null)
  const [isLoadingPayload, setIsLoadingPayload] = useState(true) // Loading state khi đang load payload
  const [payloadCaptureStatus, setPayloadCaptureStatus] = useState('Đang khởi tạo...') // Status message khi đang capture
  const messagesEndRef = useRef(null)
  const currentBotMessageRef = useRef(null)
  const hasSentStudentInfoRef = useRef(false) // Flag để tránh gửi thông tin nhiều lần
  const pendingStudentInfoRef = useRef(null) // Lưu thông tin sinh viên đã thu thập để gửi sau khi payload load xong
  
  // State cho popup thông tin sinh viên
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [isInDormitory, setIsInDormitory] = useState(null) // null: chưa chọn, true: ở KTX, false: chưa ở KTX
  const [studentName, setStudentName] = useState('')
  const [roomNumber, setRoomNumber] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [isSubmittingInfo, setIsSubmittingInfo] = useState(false)
  
  // State cho popup đánh giá
  const [showRatingModal, setShowRatingModal] = useState(false)
  const [rating, setRating] = useState(0) // 0-5
  const [feedback, setFeedback] = useState('')
  const [isSubmittingRating, setIsSubmittingRating] = useState(false)
  
  // State cho popup cảm ơn
  const [showThankYouModal, setShowThankYouModal] = useState(false)

  // Xóa các hàm không cần thiết - chỉ dùng tryAutoCaptureWithFallback
  /*
  const getCaptureScript = () => {
    return `(function() {
  console.log('🎯 Payload capture script đang chạy...');
  
  // Intercept fetch requests
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    const url = args[0];
    
    if (typeof url === 'string' && url.includes('/api/chat')) {
      const [requestUrl, options] = args;
      
      if (options && options.method === 'POST' && options.body) {
        try {
          const payload = JSON.parse(options.body);
          console.log('✅ Captured payload:', payload);
          
          // Gửi payload về parent window (nếu có)
          if (window.opener && !window.opener.closed) {
            console.log('📤 Sending payload to parent window...');
            window.opener.postMessage({
              type: 'CAPTURED_PAYLOAD',
              payload: payload
            }, '*');
            
            // Hiển thị thông báo
            const notification = document.createElement('div');
            notification.style.cssText = \`
              position: fixed;
              top: 20px;
              right: 20px;
              background: #4caf50;
              color: white;
              padding: 15px 20px;
              border-radius: 8px;
              z-index: 1000000;
              box-shadow: 0 4px 6px rgba(0,0,0,0.3);
              font-family: Arial, sans-serif;
            \`;
            notification.textContent = '✅ Đã capture payload thành công!';
            document.body.appendChild(notification);
            
            setTimeout(() => {
              notification.remove();
            }, 3000);
          } else {
            // Nếu không có opener, copy vào clipboard
            navigator.clipboard.writeText(JSON.stringify(payload, null, 2)).then(() => {
              alert('✅ Đã capture payload và copy vào clipboard!\\n\\nPaste vào app của bạn.');
              console.log('Payload đã được copy vào clipboard:', payload);
            }).catch(() => {
              console.log('Payload (copy thủ công):', JSON.stringify(payload, null, 2));
              prompt('Copy payload này:', JSON.stringify(payload, null, 2));
            });
          }
        } catch (e) {
          console.error('❌ Error capturing payload:', e);
        }
      }
    }
    
    return originalFetch.apply(this, args);
  };
  
  console.log('✅ Payload capture script đã sẵn sàng!\\nGửi một message trên trang này để capture payload.');
})();`
  }

  // Hàm để tự động capture payload qua Python Selenium backend
  const openCaptureWindow = async () => {
    try {
      // Thử gọi API tự động capture trước
      const response = await fetch(`${BACKEND_API_URL}/api/capture-payload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'hi' }),
      })

      if (response.ok) {
        console.log('✅ Auto capture started, waiting for result...')
        
        // Polling với timeout 15 giây
        const startTime = Date.now()
        const timeout = 15000 // 15 giây
        let isCompleted = false
        
        const checkStatus = async () => {
          if (isCompleted) return
          
          try {
            const statusRes = await fetch(`${BACKEND_API_URL}/api/capture-status`)
            const status = await statusRes.json()

            if (status.status === 'captured' && status.payload) {
              isCompleted = true
              // Capture thành công, lưu payload với các ID mới
              const newPayload = status.payload
              setPayloadTemplate(newPayload)
              localStorage.setItem('chatbotPayloadTemplate', JSON.stringify(newPayload))

              const notification = document.createElement('div')
              notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: #4caf50;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                z-index: 1000000;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                font-family: Arial, sans-serif;
              `
              notification.textContent = '✅ Đã tự động capture và lưu payload thành công!'
              document.body.appendChild(notification)
              setTimeout(() => notification.remove(), 3000)

              console.log('✅ Auto-captured payload với blockId:', newPayload.blockId)
              console.log('✅ Auto-captured payload với chatbotSessionId:', newPayload.chatbotSessionId)
              console.log('✅ Auto-captured payload với predictionId:', newPayload.predictionId)
              console.log('✅ Full captured payload:', newPayload)
              return
            } else if (status.status === 'error') {
              isCompleted = true
              throw new Error(status.error || 'Capture failed')
            } else if (status.status === 'capturing') {
              // Kiểm tra timeout
              if (Date.now() - startTime > timeout) {
                isCompleted = true
                throw new Error('Timeout: Capture mất quá nhiều thời gian')
              }
              // Tiếp tục polling
              setTimeout(checkStatus, 500)
              return
            }
          } catch (e) {
            if (!isCompleted) {
              isCompleted = true
              throw e
            }
          }
        }

        // Bắt đầu polling
        setTimeout(checkStatus, 500)
        
        // Set timeout tổng thể
        setTimeout(() => {
          if (!isCompleted) {
            isCompleted = true
            console.log('⏱️ Auto capture timeout, using default payload')
            useDefaultPayload()
          }
        }, timeout)
        
        return
      }
    } catch (e) {
      console.log('⚠️ Auto capture không khả dụng:', e)
    }

    // Nếu auto capture fail, tự động dùng payload mặc định
    console.log('📦 Auto capture failed, using default payload')
    useDefaultPayload()
  }

  // Phương pháp thủ công (fallback)
  const fallbackToManual = () => {
    const captureWindow = window.open(
      'https://trungtamquanlykytucxadhquocgiahcm.zapier.app/',
      'captureWindow',
      'width=1200,height=800'
    )

    if (!captureWindow) {
      alert('Popup bị chặn. Vui lòng cho phép popup và thử lại.')
      return
    }

    const script = getCaptureScript()
    
    navigator.clipboard.writeText(script).then(() => {
      alert(`✅ Đã copy script vào clipboard!\n\nHƯỚNG DẪN:\n1. Trên trang web vừa mở, nhấn F12\n2. Vào tab Console\n3. Paste (Ctrl+V) và Enter\n4. Gửi một message để capture payload`)
    }).catch(() => {
      alert('Vui lòng copy script từ ô bên dưới')
    })
  }
  */

  // Hiển thị popup thông tin sinh viên mỗi lần vào trang (hoàn toàn mới)
  useEffect(() => {
    // Luôn hiển thị popup mỗi lần vào trang, không kiểm tra localStorage
    setShowInfoModal(true)
  }, []) // Chỉ chạy 1 lần khi mount

  // Tự động gửi thông tin sinh viên đã thu thập sau khi payload load xong
  useEffect(() => {
    // Chỉ gửi khi payload đã load xong VÀ có thông tin đã thu thập VÀ chưa gửi
    if (!isLoadingPayload && payloadTemplate && !hasSentStudentInfoRef.current && pendingStudentInfoRef.current) {
      const studentInfo = pendingStudentInfoRef.current
      
      // Gửi thông tin cho bot
      hasSentStudentInfoRef.current = true
      setTimeout(() => {
        sendMessage(studentInfo.infoMessage).then(() => {
          // Gửi thành công, xóa thông tin đã gửi
          pendingStudentInfoRef.current = null
        }).catch(error => {
          console.error('Error sending student info to bot:', error)
          hasSentStudentInfoRef.current = false // Reset để có thể thử lại
        })
      }, 300) // Đợi một chút để đảm bảo chat đã render xong
    }
  }, [isLoadingPayload, payloadTemplate])

  // Bắt đầu capture payload mới mỗi lần vào trang (không load từ localStorage)
  useEffect(() => {
    const startNewCapture = () => {
      setIsLoadingPayload(true)
      setPayloadCaptureStatus('Đang khởi tạo capture...')
      
      // Luôn bắt đầu capture mới, không load từ localStorage
      console.log('🚀 Bắt đầu capture payload mới...')
      tryAutoCaptureWithFallback() // Không await để website load ngay
    }
    
    startNewCapture()
  }, []) // Chỉ chạy 1 lần khi mount

  // Hàm thử capture tự động, chỉ dùng payload mặc định khi backend trả về false/error
  const tryAutoCaptureWithFallback = async () => {
    try {
      // Gọi API capture ngay lập tức với message 'hi'
      console.log('🚀 Bắt đầu capture payload ngay lập tức...')
      const response = await fetch(`${BACKEND_API_URL}/api/capture-payload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'hi' }),
      })

      if (response.ok) {
        console.log('✅ Auto capture started, waiting for result...')
        setIsLoadingPayload(true)
        setPayloadCaptureStatus('Đang mở browser và gửi tin nhắn...')
        
        // Polling với timeout 20 giây (tăng lên một chút để đảm bảo)
        const timeout = 20000 // 20 giây
        let captureCompleted = false // Đánh dấu đã hoàn thành (thành công hoặc thất bại)
        
        const checkStatus = async () => {
          try {
            const statusRes = await fetch(`${BACKEND_API_URL}/api/capture-status`)
            const status = await statusRes.json()

            // Cập nhật status message
            if (status.message) {
              setPayloadCaptureStatus(status.message)
            }

            if (status.status === 'captured' && status.payload) {
              // Backend trả về thành công (true) → lưu payload (chỉ dùng trong session này)
              captureCompleted = true
              setPayloadTemplate(status.payload)
              // Không lưu vào localStorage để mỗi lần vào trang đều mới
              setPayloadCaptureStatus('')
              // Reset is_capturing flag trên backend
              fetch(`${BACKEND_API_URL}/api/reset-capture`, { method: 'POST' }).catch(() => {})

              const notification = document.createElement('div')
              notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: #4caf50;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                z-index: 1000000;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                font-family: Arial, sans-serif;
              `
              notification.textContent = '✅ Đã tự động capture payload thành công!'
              document.body.appendChild(notification)
              setTimeout(() => notification.remove(), 3000)

              console.log('✅ Auto-captured payload:', status.payload)
              return true
            } else if (status.status === 'error') {
              // Backend trả về lỗi (false) → dùng payload mặc định
              captureCompleted = true
              console.log('❌ Backend trả về lỗi, sử dụng payload mặc định')
              useDefaultPayload()
              // Reset is_capturing flag trên backend
              fetch(`${BACKEND_API_URL}/api/reset-capture`, { method: 'POST' }).catch(() => {})
              return true // Đánh dấu đã hoàn thành để dừng polling
            } else if (status.status === 'capturing') {
              // Backend đang xử lý → tiếp tục loading và polling
              return false // Tiếp tục polling
            }
            // Trạng thái khác (idle) → tiếp tục polling
            return false
          } catch (e) {
            // Lỗi khi gọi API status → tiếp tục thử (có thể backend đang xử lý)
            return false
          }
        }

        // Bắt đầu polling ngay lập tức với interval ngắn hơn để phản hồi nhanh
        let pollCount = 0
        const pollInterval = setInterval(async () => {
          pollCount++
          try {
            const completed = await checkStatus()
            if (completed) {
              clearInterval(pollInterval)
            }
          } catch (e) {
            // Lỗi nghiêm trọng → dừng polling và dùng payload mặc định
            clearInterval(pollInterval)
            captureCompleted = true
            console.error('❌ Lỗi nghiêm trọng khi polling:', e)
            useDefaultPayload()
          }
        }, 300) // Giảm interval xuống 300ms để phản hồi nhanh hơn
        
        // Set timeout tổng thể - chỉ dùng payload mặc định khi timeout
        setTimeout(() => {
          clearInterval(pollInterval)
          if (!captureCompleted) {
            // Timeout → backend không trả kết quả → dùng payload mặc định
            console.log('⏱️ Auto capture timeout, backend không trả kết quả, sử dụng payload mặc định')
            captureCompleted = true
            useDefaultPayload()
          }
        }, timeout)
        
        return
      } else {
        // Backend không phản hồi OK → thử kiểm tra status xem có payload từ lần trước không
        console.log('⚠️ Backend response không OK, thử kiểm tra status...')
        setIsLoadingPayload(true)
        setPayloadCaptureStatus('Đang kiểm tra backend...')
        
        // Thử kiểm tra status một lần
        try {
          const statusRes = await fetch('http://localhost:5000/api/capture-status')
          const status = await statusRes.json()
          
          if (status.status === 'captured' && status.payload) {
            // Có payload từ lần trước → dùng luôn (không lưu vào localStorage)
            setPayloadTemplate(status.payload)
            setPayloadCaptureStatus('')
            return
          } else if (status.status === 'error') {
            // Backend trả về lỗi → dùng payload mặc định
            console.log('❌ Backend trả về lỗi, sử dụng payload mặc định')
            useDefaultPayload()
            // Reset is_capturing flag trên backend
            fetch(`${BACKEND_API_URL}/api/reset-capture`, { method: 'POST' }).catch(() => {})
            return
          }
        } catch (e) {
          // Không thể kết nối backend → dùng payload mặc định
          console.log('⚠️ Không thể kết nối backend:', e)
          console.log('📦 Sử dụng payload mặc định...')
          useDefaultPayload()
          // Reset is_capturing flag trên backend
          fetch(`${BACKEND_API_URL}/api/reset-capture`, { method: 'POST' }).catch(() => {})
        }
      }
    } catch (e) {
      // Lỗi kết nối hoàn toàn → dùng payload mặc định
      console.log('⚠️ Không thể kết nối backend:', e)
      console.log('📦 Sử dụng payload mặc định...')
      useDefaultPayload()
      // Reset is_capturing flag trên backend
      fetch(`${BACKEND_API_URL}/api/reset-capture`, { method: 'POST' }).catch(() => {})
    }
  }

  // Hàm sử dụng payload mặc định
  const useDefaultPayload = () => {
    setPayloadTemplate(DEFAULT_PAYLOAD_TEMPLATE)
    // Không lưu vào localStorage để mỗi lần vào trang đều mới
    setPayloadCaptureStatus('')
    // Không set isLoadingPayload = false ở đây, để useEffect xử lý
    console.log('✅ Using default payload template')
  }
  
  // useEffect để đảm bảo isLoadingPayload chỉ được set về false sau khi payloadTemplate đã có
  useEffect(() => {
    if (payloadTemplate && isLoadingPayload) {
      // Nếu đã có payloadTemplate nhưng vẫn đang loading, set loading = false
      const timer = setTimeout(() => {
        setIsLoadingPayload(false)
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [payloadTemplate, isLoadingPayload])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Format text to markdown for better display
  const formatContent = (text) => {
    if (!text) return text
    
    // Convert patterns like "1. Đối tượng đăng ký:" to markdown headers
    let formatted = text
    
    // Convert numbered sections with colons to headers
    formatted = formatted.replace(/^(\d+\.\s+[^:]+:)/gm, '### $1')
    
    // Convert patterns like "- item" or "• item" to markdown lists if they're at start of line
    formatted = formatted.replace(/^[\u2022\u2023\u25E6\u2043\-\*]\s+(.+)$/gm, '- $1')
    
    // Ensure proper spacing between sections
    formatted = formatted.replace(/\n\n+/g, '\n\n')
    
    return formatted
  }

  const parseStreamLine = (line) => {
    // Handle empty lines
    if (!line || !line.trim()) return null

    // Parse text chunks: 0:"text"
    if (line.startsWith('0:')) {
      // Handle escaped quotes in JSON string
      try {
        const jsonStr = line.substring(2)
        const content = JSON.parse(jsonStr)
        return { type: 'text', content: content }
      } catch (e) {
        // Fallback: try regex extraction
        const match = line.match(/^0:"((?:[^"\\]|\\.)*)"/)
        if (match) {
          return { type: 'text', content: match[1].replace(/\\"/g, '"').replace(/\\\\/g, '\\') }
        }
        return null
      }
    } 
    // Parse message ID: f:{...}
    else if (line.startsWith('f:')) {
      try {
        const json = JSON.parse(line.substring(2))
        return { type: 'messageId', data: json }
      } catch (e) {
        console.warn('Failed to parse f: line:', line)
        return null
      }
    } 
    // Parse finish events: e:{...}
    else if (line.startsWith('e:')) {
      try {
        const json = JSON.parse(line.substring(2))
        return { type: 'finish', data: json }
      } catch (e) {
        console.warn('Failed to parse e: line:', line)
        return null
      }
    } 
    // Parse final data: d:{...}
    else if (line.startsWith('d:')) {
      try {
        const json = JSON.parse(line.substring(2))
        return { type: 'data', data: json }
      } catch (e) {
        console.warn('Failed to parse d: line:', line)
        return null
      }
    } 
    // Parse session info: 2:{...}
    else if (line.startsWith('2:')) {
      try {
        const json = JSON.parse(line.substring(2))
        return { type: 'session', data: json }
      } catch (e) {
        console.warn('Failed to parse 2: line:', line)
        return null
      }
    }
    
    return null
  }

  const sendMessage = async (content) => {
    if (!content.trim() || isLoading || !payloadTemplate) return

    const userMessage = {
      id: Date.now(),
      content: content.trim(),
      isUser: true
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Add placeholder bot message
    const botMessageId = Date.now() + 1
    const botMessage = {
      id: botMessageId,
      content: '',
      isUser: false
    }
    setMessages(prev => [...prev, botMessage])

    // Tạo payload từ template, chỉ thay đổi message.content
    // Đảm bảo các ID được cập nhật từ payload template mới nhất
    const requestPayload = {
      ...payloadTemplate,
      message: {
        ...payloadTemplate.message,
        content: content.trim()
      }
    }
    
    // Log để debug
    console.log('Request payload với blockId:', requestPayload.blockId)
    console.log('Request payload với chatbotSessionId:', requestPayload.chatbotSessionId)
    console.log('Request payload với predictionId:', requestPayload.predictionId)

    try {
      console.log('Sending request to:', API_URL)
      console.log('Payload:', requestPayload)

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', Object.fromEntries(response.headers.entries()))

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }

      // Check if response body exists
      if (!response.body) {
        throw new Error('Response body is null')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      let accumulatedContent = ''
      let isFinished = false

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          console.log('Stream finished')
          break
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true })
        
        // Split by newlines, but keep incomplete lines in buffer
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        // Process each complete line
        for (const line of lines) {
          const trimmedLine = line.trim()
          if (!trimmedLine) continue
          
          console.log('Received line:', trimmedLine)
          
          const parsed = parseStreamLine(trimmedLine)
          if (!parsed) {
            console.warn('Could not parse line:', trimmedLine)
            continue
          }

          // Handle text chunks
          if (parsed.type === 'text') {
            accumulatedContent += parsed.content
            setMessages(prev => prev.map(msg => 
              msg.id === botMessageId 
                ? { ...msg, content: accumulatedContent }
                : msg
            ))
          } 
          // Handle finish event - continue streaming if isContinued is true
          else if (parsed.type === 'finish') {
            console.log('Finish event:', parsed.data)
            if (parsed.data.finishReason === 'stop' && !parsed.data.isContinued) {
              isFinished = true
            }
          }
          // Handle final data
          else if (parsed.type === 'data') {
            console.log('Data event:', parsed.data)
            if (parsed.data.finishReason === 'stop') {
              isFinished = true
            }
          }
          // Handle session info - cập nhật chatbotSessionId từ response
          else if (parsed.type === 'session') {
            console.log('Session info:', parsed.data)
            // Nếu có chatbotSessionId mới từ response, cập nhật vào payload template
            if (parsed.data && Array.isArray(parsed.data) && parsed.data.length > 0) {
              const sessionData = parsed.data[0]
              if (sessionData.chatbotSessionId) {
                console.log('🔄 Updating chatbotSessionId from response:', sessionData.chatbotSessionId)
                setPayloadTemplate(prev => {
                  if (prev) {
                    const updated = {
                      ...prev,
                      chatbotSessionId: sessionData.chatbotSessionId,
                      id: sessionData.chatbotSessionId // Cập nhật id nếu có
                    }
                    // Lưu vào localStorage để dùng cho lần sau
                    localStorage.setItem('chatbotPayloadTemplate', JSON.stringify(updated))
                    return updated
                  }
                  return prev
                })
              }
            }
          }
          // Handle message ID
          else if (parsed.type === 'messageId') {
            console.log('Message ID:', parsed.data)
          }
        }

        // Stop if finished
        if (isFinished) {
          break
        }
      }

      // Handle any remaining content in buffer
      if (buffer.trim()) {
        const parsed = parseStreamLine(buffer.trim())
        if (parsed && parsed.type === 'text') {
          accumulatedContent += parsed.content
          setMessages(prev => prev.map(msg => 
            msg.id === botMessageId 
              ? { ...msg, content: accumulatedContent }
              : msg
          ))
        }
      }

      // If no content was received, show a message
      if (!accumulatedContent.trim()) {
        setMessages(prev => prev.map(msg => 
          msg.id === botMessageId 
            ? { ...msg, content: 'Không nhận được phản hồi từ server' }
            : msg
        ))
      }

    } catch (error) {
      console.error('Error details:', error)
      console.error('Error name:', error.name)
      console.error('Error message:', error.message)
      console.error('Error stack:', error.stack)
      
      let errorMessage = 'Đã xảy ra lỗi'
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet hoặc CORS policy.'
      } else if (error.message) {
        errorMessage = `Lỗi: ${error.message}`
      }
      
      setMessages(prev => prev.map(msg => 
        msg.id === botMessageId 
          ? { ...msg, content: errorMessage, isError: true }
          : msg
      ))
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage(inputValue)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(inputValue)
    }
  }

  // Hàm xử lý submit thông tin sinh viên
  const handleSubmitStudentInfo = async (e) => {
    e.preventDefault()
    
    if (!studentName.trim()) {
      alert('Vui lòng nhập họ và tên')
      return
    }
    
    if (isInDormitory === true && !roomNumber.trim()) {
      alert('Vui lòng nhập số phòng')
      return
    }
    
    if (isInDormitory === false && !phoneNumber.trim()) {
      alert('Vui lòng nhập số điện thoại')
      return
    }
    
    setIsSubmittingInfo(true)
    
    // Không lưu thông tin vào localStorage để mỗi lần vào trang đều mới
    // Chỉ dùng thông tin trong session này
    
    // Tạo thông báo để gửi cho bot
    let infoMessage = ''
    if (isInDormitory) {
      infoMessage = `Xin chào, tôi là ${studentName}, hiện đang ở Ký túc xá, phòng ${roomNumber}.`
    } else {
      infoMessage = `Xin chào, tôi là ${studentName}, hiện chưa ở Ký túc xá. Số điện thoại của tôi là ${phoneNumber}.`
    }
    
    // Đóng modal trước
    setShowInfoModal(false)
    setIsSubmittingInfo(false)
    
    // Lưu thông tin vào ref để gửi sau khi payload load xong
    pendingStudentInfoRef.current = {
      isInDormitory,
      name: studentName.trim(),
      roomNumber: isInDormitory ? roomNumber.trim() : null,
      phoneNumber: isInDormitory ? null : phoneNumber.trim(),
      infoMessage
    }
    
    // Gửi thông tin cho bot (chờ payload sẵn sàng)
    if (payloadTemplate && !isLoadingPayload) {
      // Nếu payload đã sẵn sàng, gửi ngay
      try {
        hasSentStudentInfoRef.current = true
        await sendMessage(infoMessage)
        pendingStudentInfoRef.current = null // Xóa thông tin đã gửi
      } catch (error) {
        console.error('Error sending student info to bot:', error)
        hasSentStudentInfoRef.current = false
      }
    } else {
      // Nếu payload chưa sẵn sàng, đánh dấu để gửi sau khi payload load xong
      hasSentStudentInfoRef.current = false
      console.log('Thông tin đã được lưu, sẽ tự động gửi khi payload load xong')
    }
  }

  // Hàm xử lý mở popup đánh giá
  const handleEndChat = () => {
    setShowRatingModal(true)
  }

  // Hàm xử lý submit đánh giá
  const handleSubmitRating = async (e) => {
    e.preventDefault()
    
    if (rating === 0) {
      alert('Vui lòng chọn số sao đánh giá')
      return
    }
    
    setIsSubmittingRating(true)
    
    // Lưu đánh giá vào localStorage
    const ratingData = {
      rating,
      feedback: feedback.trim(),
      timestamp: new Date().toISOString(),
      messageCount: messages.length
    }
    
    // Lấy danh sách đánh giá cũ (nếu có)
    const savedRatings = JSON.parse(localStorage.getItem('chatRatings') || '[]')
    savedRatings.push(ratingData)
    localStorage.setItem('chatRatings', JSON.stringify(savedRatings))
    
    // Tạo tin nhắn đánh giá để gửi vào chat
    const stars = '⭐'.repeat(rating) + '☆'.repeat(5 - rating)
    let ratingMessage = `Đánh giá dịch vụ: ${stars} (${rating}/5 sao)`
    if (feedback.trim()) {
      ratingMessage += `\n\nGóp ý: ${feedback.trim()}`
    }
    
    // Gửi đánh giá vào chat
    try {
      if (payloadTemplate) {
        await sendMessage(ratingMessage)
      } else {
        // Nếu chưa có payload, thêm vào messages trực tiếp
        const userRatingMessage = {
          id: Date.now(),
          content: ratingMessage,
          isUser: true
        }
        setMessages(prev => [...prev, userRatingMessage])
      }
    } catch (error) {
      console.error('Error sending rating to chat:', error)
      // Vẫn hiển thị popup cảm ơn dù có lỗi
    }
    
    console.log('Đánh giá đã được lưu:', ratingData)
    
    // Đóng modal đánh giá và hiển thị popup cảm ơn
    setShowRatingModal(false)
    setRating(0)
    setFeedback('')
    setIsSubmittingRating(false)
    
    // Đợi một chút để tin nhắn được gửi xong trước khi hiển thị popup cảm ơn
    setTimeout(() => {
      setShowThankYouModal(true)
    }, 500)
  }

  // Hàm quay lại chat
  const handleBackToChat = () => {
    setShowThankYouModal(false)
  }

  // Hàm về trang chủ
  const handleGoHome = () => {
    // Có thể redirect về trang chủ hoặc reload trang
    window.location.href = '/'
    // Hoặc nếu muốn reset toàn bộ:
    // localStorage.removeItem('studentInfo')
    // window.location.reload()
  }


  // Hiển thị loading screen khi đang load payload (nhưng vẫn cho phép popup thông tin hiển thị)
  const loadingScreen = isLoadingPayload ? (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 9999
    }}>
      <div className="loading-spinner" style={{
        width: '50px',
        height: '50px',
        border: '4px solid rgba(255, 255, 255, 0.3)',
        borderTop: '4px solid white',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '20px'
      }}></div>
      <h2 style={{ marginBottom: '10px' }}>Đang tải chatbot...</h2>
      <p style={{ opacity: 0.8 }}>{payloadCaptureStatus || 'Đang khởi tạo...'}</p>
    </div>
  ) : null

  return (
    <>
      {/* Loading screen khi đang load payload */}
      {loadingScreen}
      
      {/* Modal thông tin sinh viên - có thể hiển thị ngay cả khi đang loading */}
      {showInfoModal && (
        <div className="info-modal-overlay" onClick={(e) => {
          // Không cho đóng khi click vào overlay, phải điền form
          if (e.target === e.currentTarget) {
            return
          }
        }}>
          <div className="info-modal" onClick={(e) => e.stopPropagation()}>
            <div className="info-modal-header">
              <h2>Thông tin sinh viên</h2>
              <p>Vui lòng cung cấp thông tin để chúng tôi phục vụ bạn tốt hơn</p>
            </div>
            <form onSubmit={handleSubmitStudentInfo} className="info-modal-form">
              <div className="info-modal-question">
                <label>Bạn có đang ở Ký túc xá không?</label>
                <div className="info-modal-options">
                  <button
                    type="button"
                    className={`info-modal-option ${isInDormitory === true ? 'active' : ''}`}
                    onClick={() => setIsInDormitory(true)}
                  >
                    Có, tôi đang ở KTX
                  </button>
                  <button
                    type="button"
                    className={`info-modal-option ${isInDormitory === false ? 'active' : ''}`}
                    onClick={() => setIsInDormitory(false)}
                  >
                    Chưa, tôi chưa ở KTX
                  </button>
                </div>
              </div>

              {isInDormitory !== null && (
                <>
                  <div className="info-modal-field">
                    <label htmlFor="studentName">Họ và tên *</label>
                    <input
                      type="text"
                      id="studentName"
                      value={studentName}
                      onChange={(e) => setStudentName(e.target.value)}
                      placeholder="Nhập họ và tên của bạn"
                      required
                      disabled={isSubmittingInfo}
                    />
                  </div>

                  {isInDormitory ? (
                    <div className="info-modal-field">
                      <label htmlFor="roomNumber">Số phòng *</label>
                      <input
                        type="text"
                        id="roomNumber"
                        value={roomNumber}
                        onChange={(e) => setRoomNumber(e.target.value)}
                        placeholder="Ví dụ: A101, B205"
                        required
                        disabled={isSubmittingInfo}
                      />
                    </div>
                  ) : (
                    <div className="info-modal-field">
                      <label htmlFor="phoneNumber">Số điện thoại *</label>
                      <input
                        type="tel"
                        id="phoneNumber"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        placeholder="Nhập số điện thoại của bạn"
                        required
                        disabled={isSubmittingInfo}
                      />
                    </div>
                  )}

                  <div className="info-modal-actions">
                    <button
                      type="submit"
                      className="info-modal-submit"
                      disabled={isSubmittingInfo}
                    >
                      {isSubmittingInfo ? 'Đang gửi...' : 'Xác nhận'}
                    </button>
                  </div>
                </>
              )}
            </form>
          </div>
        </div>
      )}

      {/* Modal đánh giá */}
      {showRatingModal && (
        <div className="rating-modal-overlay" onClick={(e) => {
          // Không cho đóng khi click vào overlay, phải đánh giá
          if (e.target === e.currentTarget) {
            return
          }
        }}>
          <div className="rating-modal" onClick={(e) => e.stopPropagation()}>
            <div className="rating-modal-header">
              <h2>Đánh giá trải nghiệm</h2>
              <p>Cảm ơn bạn đã sử dụng dịch vụ! Vui lòng đánh giá trải nghiệm của bạn</p>
            </div>
            <form onSubmit={handleSubmitRating} className="rating-modal-form">
              <div className="rating-modal-stars">
                <label>Đánh giá của bạn *</label>
                <div className="stars-container">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      className={`star-button ${rating >= star ? 'active' : ''}`}
                      onClick={() => setRating(star)}
                      onMouseEnter={() => {
                        // Highlight stars on hover
                        if (!isSubmittingRating) {
                          // Optional: add hover effect
                        }
                      }}
                      disabled={isSubmittingRating}
                    >
                      <svg
                        width="40"
                        height="40"
                        viewBox="0 0 24 24"
                        fill={rating >= star ? '#FFD700' : 'none'}
                        stroke={rating >= star ? '#FFD700' : '#ccc'}
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                      </svg>
                    </button>
                  ))}
                </div>
                {rating > 0 && (
                  <p className="rating-text">
                    {rating === 1 && 'Rất không hài lòng'}
                    {rating === 2 && 'Không hài lòng'}
                    {rating === 3 && 'Bình thường'}
                    {rating === 4 && 'Hài lòng'}
                    {rating === 5 && 'Rất hài lòng'}
                  </p>
                )}
              </div>

              <div className="rating-modal-field">
                <label htmlFor="feedback">Góp ý của bạn (tùy chọn)</label>
                <textarea
                  id="feedback"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Chia sẻ ý kiến của bạn để chúng tôi cải thiện dịch vụ..."
                  rows="4"
                  disabled={isSubmittingRating}
                />
              </div>

              <div className="rating-modal-actions">
                <button
                  type="button"
                  className="rating-modal-cancel"
                  onClick={() => {
                    if (!isSubmittingRating) {
                      setShowRatingModal(false)
                      setRating(0)
                      setFeedback('')
                    }
                  }}
                  disabled={isSubmittingRating}
                >
                  Bỏ qua
                </button>
                <button
                  type="submit"
                  className="rating-modal-submit"
                  disabled={isSubmittingRating || rating === 0}
                >
                  {isSubmittingRating ? 'Đang gửi...' : 'Gửi đánh giá'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal cảm ơn */}
      {showThankYouModal && (
        <div className="thank-you-modal-overlay">
          <div className="thank-you-modal">
            <div className="thank-you-icon">
              <svg
                width="80"
                height="80"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#4caf50"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <h2>Cảm ơn bạn!</h2>
            <p>Đánh giá của bạn đã được gửi thành công.</p>
            <p className="thank-you-subtitle">Chúng tôi rất trân trọng ý kiến đóng góp của bạn!</p>
            <div className="thank-you-actions">
              <button
                className="thank-you-button back-to-chat"
                onClick={handleBackToChat}
              >
                Quay lại đoạn chat
              </button>
              <button
                className="thank-you-button go-home"
                onClick={handleGoHome}
              >
                Về lại trang chủ
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chỉ hiển thị khung chat sau khi payload đã load xong */}
      {!isLoadingPayload && payloadTemplate && (
        <div className="chat-container">
        <div className="chat-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
            <span>💬 Chatbot Test</span>
            <button
              className="end-chat-button"
              onClick={handleEndChat}
              title="Kết thúc chat và đánh giá"
            >
              Kết thúc chat
            </button>
          </div>
        </div>
      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.isUser ? 'user' : 'bot'} ${message.isError ? 'error' : ''}`}
          >
            {message.isUser ? (
              <span>{message.content}</span>
            ) : (
              message.content ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  className="markdown-content"
                >
                  {formatContent(message.content)}
                </ReactMarkdown>
              ) : (
                <span>Đang gõ...</span>
              )
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-container" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder='Nhập tin nhắn của bạn...'
          disabled={isLoading}
          autoComplete="off"
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !inputValue.trim()}
        >
          Gửi
        </button>
      </form>
        </div>
      )}
    </>
  )
}

export default App


