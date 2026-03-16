<script setup>
import { ref, onMounted } from 'vue'

// Состояние
const accounts = ref([])
const scripts = ref([])
const topic = ref('')
const selectedAccount = ref(null)
const isLoading = ref(false)
const isFetching = ref(true)

// Состояние видео-плеера
const showVideoModal = ref(false)
const currentVideoUrl = ref('')
const processingScripts = ref(new Set())

// API URL
const API_BASE = 'http://localhost:8000/api'
const MEDIA_BASE = 'http://localhost:8000/media'

// Загрузка данных
const fetchData = async () => {
  try {
    const [accRes, scriptRes] = await Promise.all([
      fetch(`${API_BASE}/accounts/`),
      fetch(`${API_BASE}/scripts/`)
    ])
    accounts.value = await accRes.json()
    scripts.value = await scriptRes.json()
    if (accounts.value.length > 0) selectedAccount.value = accounts.value[0].id
    
    // Проверяем статусы обработки
    scripts.value.forEach(s => {
      if (s.status === 'processing') {
        startPolling(s.id)
      }
    })
  } catch (e) {
    console.error("Ошибка загрузки данных:", e)
  } finally {
    isFetching.value = false
  }
}

// Генерация сценария
const generateScript = async () => {
  if (!topic.value.trim()) return
  isLoading.value = true
  
  try {
    const response = await fetch(`${API_BASE}/generate/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        topic: topic.value,
        account_id: selectedAccount.value 
      })
    })
    
    if (response.ok) {
      const newScript = await response.json()
      scripts.value.unshift(newScript)
      if (scripts.value.length > 5) scripts.value.pop()
      topic.value = ''
    }
  } catch (e) {
    console.error("Ошибка генерации:", e)
  } finally {
    isLoading.value = false
  }
}

// Сборка видео
const assembleVideo = async (scriptId) => {
  try {
    const response = await fetch(`${API_BASE}/generate-video/${scriptId}/`, {
      method: 'POST'
    })
    if (response.ok) {
      const scriptIndex = scripts.value.findIndex(s => s.id === scriptId)
      if (scriptIndex !== -1) {
        scripts.value[scriptIndex].status = 'processing'
        startPolling(scriptId)
      }
    }
  } catch (e) {
    console.error("Ошибка запуска сборки видео:", e)
  }
}

// Опрос статуса видео
const startPolling = (scriptId) => {
  if (processingScripts.value.has(scriptId)) return
  processingScripts.value.add(scriptId)
  
  const poll = async () => {
    try {
      const response = await fetch(`${API_BASE}/scripts/${scriptId}/`)
      const data = await response.json()
      
      const scriptIndex = scripts.value.findIndex(s => s.id === scriptId)
      if (scriptIndex !== -1) {
        scripts.value[scriptIndex] = data
        
        if (data.status === 'completed' || data.status === 'failed') {
          processingScripts.value.delete(scriptId)
          return // Стоп опрос
        }
      }
      setTimeout(poll, 3000)
    } catch (e) {
      console.error("Ошибка опроса статуса:", e)
      processingScripts.value.delete(scriptId)
    }
  }
  poll()
}

// Показ видео
const openVideo = (videoPath) => {
  currentVideoUrl.value = `${MEDIA_BASE}/${videoPath}`
  showVideoModal.value = true
}

onMounted(fetchData)
</script>

<template>
  <div class="min-h-screen bg-[#0d1117] text-slate-200 font-sans flex flex-col md:flex-row">
    
    <!-- Sidebar (Accounts) -->
    <aside class="w-full md:w-80 bg-[#161b22] border-r border-slate-800 p-6 flex flex-col gap-8">
      <div class="flex items-center gap-3 px-2">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white">M</div>
        <h1 class="text-xl font-bold tracking-tight text-white">AiMedia Health</h1>
      </div>

      <nav class="flex flex-col gap-6">
        <div>
          <h2 class="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 px-2">Клиники на контроле</h2>
          <div v-if="isFetching" class="space-y-3 px-2">
            <div v-for="i in 3" :key="i" class="h-12 bg-slate-800 rounded-xl animate-pulse"></div>
          </div>
          <div v-else class="flex flex-col gap-1">
            <button 
              v-for="acc in accounts" 
              :key="acc.id"
              @click="selectedAccount = acc.id"
              class="flex items-center justify-between p-3 rounded-xl transition-all text-left"
              :class="selectedAccount === acc.id ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20' : 'hover:bg-slate-800 text-slate-400 border border-transparent'"
            >
              <div class="flex flex-col">
                <span class="font-medium">{{ acc.name }}</span>
                <span class="text-[10px] opacity-60 uppercase tracking-tighter">{{ acc.platform }}</span>
              </div>
              <div class="w-2 h-2 rounded-full" :class="acc.status === 'active' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-slate-600'"></div>
            </button>
          </div>
        </div>

        <div class="mt-auto pt-6 border-t border-slate-800">
           <div class="bg-slate-800/50 rounded-2xl p-4 border border-slate-700/50">
             <div class="text-[10px] uppercase font-bold text-slate-500 mb-2">Статус системы</div>
             <div class="flex items-center gap-2 text-sm text-green-400">
               <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
               AI Модуль активен
             </div>
           </div>
        </div>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-6 md:p-10 flex flex-col gap-10 overflow-y-auto">
      
      <!-- Header / Action -->
      <header class="max-w-4xl">
        <div class="flex flex-col gap-2 mb-8">
          <h2 class="text-3xl font-bold text-white tracking-tight">Маркетинговый Dashboard</h2>
          <p class="text-slate-400">Генерация AI-сценариев для Reels и TikTok клиник.</p>
        </div>

        <div class="relative group">
          <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500"></div>
          <div class="relative flex flex-col md:flex-row gap-2 p-1.5 bg-[#161b22] rounded-2xl border border-slate-700 shadow-2xl">
            <input 
              v-model="topic"
              @keyup.enter="generateScript"
              type="text" 
              placeholder="Введите тему процедуры (например: 'Отбеливание зубов')..." 
              class="flex-1 bg-transparent px-6 py-4 outline-none text-white placeholder:text-slate-600 font-medium"
              :disabled="isLoading"
            />
            <button 
              @click="generateScript"
              :disabled="isLoading || !topic.trim()"
              class="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 px-8 py-4 rounded-xl font-bold text-white transition-all flex items-center justify-center gap-3 min-w-[200px]"
            >
              <svg v-if="isLoading" class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isLoading ? 'Генерация...' : 'Создать сценарий' }}
            </button>
          </div>
        </div>
      </header>

      <!-- Scripts Feed -->
      <section class="max-w-4xl space-y-8">
        <div class="flex items-center justify-between px-2">
          <h3 class="text-lg font-bold text-slate-300">Последние сценарии</h3>
          <span class="text-xs font-medium text-slate-500">Показано: {{ scripts.length }} из 5</span>
        </div>

        <div v-if="scripts.length === 0 && !isFetching" class="bg-[#161b22] rounded-3xl p-12 text-center border border-dashed border-slate-700">
           <div class="text-slate-500 italic">Пока нет сгенерированных сценариев. Введите тему выше.</div>
        </div>

        <div v-else class="grid grid-cols-1 gap-6">
          <article 
            v-for="script in scripts" 
            :key="script.id"
            class="bg-[#161b22] border border-slate-800 rounded-3xl p-8 hover:border-slate-700 transition-all group"
          >
            <div class="flex flex-col md:flex-row gap-6">
              <div class="flex-1 space-y-4">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                    <span class="bg-blue-600/20 text-blue-400 text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded">REELS</span>
                    <span class="text-xs text-slate-500">{{ script.account_name }}</span>
                  </div>
                  
                  <!-- Статус видео -->
                  <div v-if="script.status === 'processing'" class="flex items-center gap-2">
                    <span class="text-[10px] font-bold text-blue-400 animate-pulse uppercase tracking-widest">Рендеринг...</span>
                    <div class="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div class="h-full bg-blue-500 animate-[progress_2s_ease-in-out_infinite]"></div>
                    </div>
                  </div>
                </div>

                <h4 class="text-2xl font-bold text-white group-hover:text-blue-400 transition-colors">{{ script.title }}</h4>
                <p class="text-slate-400 leading-relaxed bg-[#0d1117] p-5 rounded-2xl border border-slate-800/50 whitespace-pre-line italic">
                  "{{ script.script_text }}"
                </p>

                <div class="flex items-center justify-between pt-2">
                   <div class="text-[10px] font-bold text-slate-600 uppercase">{{ new Date(script.created_at).toLocaleString() }}</div>
                   
                   <div class="flex items-center gap-4">
                      <!-- Кнопка сборки видео -->
                      <button 
                        v-if="script.status === 'pending' || script.status === 'failed'"
                        @click="assembleVideo(script.id)"
                        class="flex items-center gap-2 text-xs font-bold text-blue-500 hover:text-blue-400 uppercase tracking-wider group/btn"
                      >
                        🎥 <span class="group-hover/btn:underline">Собрать видео</span>
                      </button>
                      
                      <!-- Кнопка просмотра видео -->
                      <button 
                        v-if="script.status === 'completed'"
                        @click="openVideo(script.video_file)"
                        class="flex items-center gap-2 text-xs font-bold text-green-500 hover:text-green-400 uppercase tracking-wider group/btn"
                      >
                        ▶️ <span class="group-hover/btn:underline">Смотреть результат</span>
                      </button>

                      <button class="text-xs font-bold text-slate-500 hover:text-slate-300 uppercase tracking-wider">Копировать</button>
                   </div>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>

    <!-- Video Modal -->
    <div v-if="showVideoModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-10">
      <div class="absolute inset-0 bg-black/90 backdrop-blur-sm" @click="showVideoModal = false"></div>
      <div class="relative bg-[#161b22] rounded-3xl overflow-hidden border border-slate-800 shadow-2xl max-w-sm w-full">
        <div class="p-4 border-b border-slate-800 flex justify-between items-center bg-[#1c2128]">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">AI Video Preview</span>
          <button @click="showVideoModal = false" class="text-slate-500 hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="aspect-[9/16] bg-black">
          <video :src="currentVideoUrl" controls autoplay class="w-full h-full object-contain"></video>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Скрываем скроллбар для чистого вида */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #21262d;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #30363d;
}

@keyframes progress {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0); }
  100% { transform: translateX(100%); }
}
</style>
