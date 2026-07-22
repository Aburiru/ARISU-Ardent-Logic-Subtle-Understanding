import React, { useState, useEffect, useRef } from 'react';
import {
  Volume2,
  VolumeX,
  MessageSquare,
  Activity,
  Cpu,
  Sparkles,
  Sliders,
  Terminal,
  Zap,
  RotateCcw,
  Sun,
  Moon,
  X,
  Send,
  Radio,
  BarChart2,
  ShieldCheck,
  Power,
  Mic,
  MicOff,
  Waves,
  Volume1
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'arisu';
  text: string;
  thought?: string; // ponytail: added for thought block visibility
  timestamp: string;
}

export default function App() {
  // Theme state: 'light' (matching exact reference screenshot) vs 'dark'
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  
  // Interactive state
  const [isAudioMuted, setIsAudioMuted] = useState<boolean>(false);
  const [isTerminalOpen, setIsTerminalOpen] = useState<boolean>(false);
  const [isDiagnosticsOpen, setIsDiagnosticsOpen] = useState<boolean>(false);
  
  // Voice & Speech State
  const [isVoiceEnabled, setIsVoiceEnabled] = useState<boolean>(true);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isListening, setIsListening] = useState<boolean>(false);
  const recognitionRef = useRef<any>(null);

  // Controls
  const [coreSpeed, setCoreSpeed] = useState<number>(1); // multiplier 1x to 3x
  const [starCount, setStarCount] = useState<number>(35);
  const [syncRate, setSyncRate] = useState<number>(98.4);
  const [memAllocated, setMemAllocated] = useState<number>(4096); // MB
  const [corePulseRate, setCorePulseRate] = useState<number>(72); // BPM
  
  // Audio synth context
  const audioCtxRef = useRef<AudioContext | null>(null);

  // Time & System metrics
  const [currentTime, setCurrentTime] = useState<string>('');
  const [millisec, setMillisec] = useState<number>(0);
  const [fps, setFps] = useState<number>(60);

  // Chat State
  const [chatInput, setChatInput] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'arisu',
      text: 'ARISU_v1.0 Neural Core initialized. Voice interface ready. How can I assist your parameters today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  ]);
  const [isThinking, setIsThinking] = useState<boolean>(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Speech Synthesis (TTS) - ARISU Speaks
  const speakResponse = (text: string) => {
    if (!isVoiceEnabled || isAudioMuted) return;

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(v => 
        v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha') || v.lang.startsWith('en')
      );
      if (preferredVoice) utterance.voice = preferredVoice;

      utterance.rate = 1.05;
      utterance.pitch = 1.1;

      utterance.onstart = () => {
        setIsSpeaking(true);
        playPulseSound(784, 'sine', 0.2);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
      };

      utterance.onerror = () => {
        setIsSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    } else {
      // Visual simulation fallback
      setIsSpeaking(true);
      setTimeout(() => setIsSpeaking(false), 4000);
    }
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // Microphone Speech Recognition - User Speaks
  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      handleDemoVoiceTalk();
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        playPulseSound(659.25, 'triangle', 0.25);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          handleSendMessage(transcript);
        }
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e) {
      handleDemoVoiceTalk();
    }
  };

  // Demo Voice trigger to showcase glowing expanded core speech instantly
  const handleDemoVoiceTalk = () => {
    const demoTexts = [
      "ARISU Neural Core online. Audio modulation synced. Visual core expanded to maximum intensity.",
      "Neural link established. Expanding holographic memory matrix to maximum bandwidth.",
      "Greetings Operator. Visual voice transmitter active. Core resonance at ninety nine percent."
    ];
    const randomText = demoTexts[Math.floor(Math.random() * demoTexts.length)];
    setChatHistory(prev => [
      ...prev,
      {
        id: `demo-${Date.now()}`,
        sender: 'arisu',
        text: randomText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      }
    ]);
    speakResponse(randomText);
  };

  // Sound Synthesizer function
  const playPulseSound = (freq = 220, type: OscillatorType = 'sine', duration = 0.15) => {
    if (isAudioMuted) return;
    try {
      if (!audioCtxRef.current) {
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        if (AudioCtx) {
          audioCtxRef.current = new AudioCtx();
        }
      }
      if (audioCtxRef.current && audioCtxRef.current.state === 'suspended') {
        audioCtxRef.current.resume();
      }
      if (!audioCtxRef.current) return;

      const osc = audioCtxRef.current.createOscillator();
      const gain = audioCtxRef.current.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtxRef.current.currentTime);
      
      // Envelope
      gain.gain.setValueAtTime(0.08, audioCtxRef.current.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtxRef.current.currentTime + duration);

      osc.connect(gain);
      gain.connect(audioCtxRef.current.destination);

      osc.start();
      osc.stop(audioCtxRef.current.currentTime + duration);
    } catch (e) {
      // Ignore audio autoplay restrictions
    }
  };

  // Clock tick & subtle telemetry fluctuations
  useEffect(() => {
    const timeInterval = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-US', { hour12: false }));
      setMillisec(Math.floor(now.getMilliseconds() / 10));
    }, 40);

    const telemetryInterval = setInterval(() => {
      setSyncRate(prev => Number((98 + Math.random() * 1.8).toFixed(1)));
      setCorePulseRate(prev => Math.floor(68 + Math.random() * 10));
      setFps(prev => Math.floor(58 + Math.random() * 4));
    }, 2000);

    return () => {
      clearInterval(timeInterval);
      clearInterval(telemetryInterval);
    };
  }, []);

  // Scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isTerminalOpen]);

  // Send message to Gemini server API
  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || chatInput).trim();
    if (!query || isThinking) return;

    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };

    setChatHistory(prev => [...prev, userMsg]);
    if (!textToSend) setChatInput('');
    setIsThinking(true);
    playPulseSound(440, 'triangle', 0.1);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          systemInstruction: 'You are ARISU_v1.0, an advanced tactical cyberpunk Neural Core AI. Respond in a concise, futuristic, precise sci-fi interface tone with system status references (e.g. Core Sync, Memory buffers).'
        })
      });

      const data = await response.json();
      const arisuText = data.text || 'Neural response buffer overflow. Query acknowledged.';

      const arisuMsg: ChatMessage = {
        id: `ari-${Date.now()}`,
        sender: 'arisu',
        text: arisuText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      };

      setChatHistory(prev => [...prev, arisuMsg]);
      playPulseSound(880, 'sine', 0.2);
      speakResponse(arisuText);
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'arisu',
        text: 'SYSTEM NOTICE: Local connection to Neural Subnet active. Core standing by.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      };
      setChatHistory(prev => [...prev, errorMsg]);
    } finally {
      setIsThinking(false);
    }
  };

  // Generate star positions deterministically
  const stars = React.useMemo(() => {
    const items = [];
    for (let i = 0; i < starCount; i++) {
      const top = (i * 17 + 7) % 95;
      const left = (i * 23 + 11) % 95;
      const duration = 2 + (i % 4) * 0.8;
      const delay = (i % 5) * 0.5;
      const isPink = i % 3 === 0;
      const size = (i % 2 === 0) ? 'w-1 h-1' : 'w-0.5 h-0.5';
      items.push({ id: i, top, left, duration, delay, isPink, size });
    }
    return items;
  }, [starCount]);

  const handleCoreClick = () => {
    playPulseSound(587.33, 'sine', 0.3); // D5 note
    if (!isSpeaking) {
      handleDemoVoiceTalk();
    } else {
      stopSpeaking();
    }
  };

  return (
    <div
      className={`w-screen h-screen relative font-space transition-colors duration-500 overflow-hidden select-none ${
        themeMode === 'light'
          ? 'bg-white text-[#131313]'
          : 'bg-[#131313] text-[#e5e2e1]'
      }`}
      style={{
        backgroundColor: themeMode === 'light' ? '#ffffff' : '#131313',
        backgroundImage: themeMode === 'light'
          ? 'radial-gradient(circle at 30% 40%, rgba(255, 75, 137, 0.03) 0%, transparent 50%), radial-gradient(circle at 70% 60%, rgba(255, 75, 137, 0.02) 0%, transparent 40%), linear-gradient(to right, rgba(254, 228, 0, 0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(254, 228, 0, 0.04) 1px, transparent 1px)'
          : 'radial-gradient(circle at 30% 40%, rgba(255, 75, 137, 0.08) 0%, transparent 50%), radial-gradient(circle at 70% 60%, rgba(254, 228, 0, 0.06) 0%, transparent 40%), linear-gradient(to right, rgba(254, 228, 0, 0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(254, 228, 0, 0.03) 1px, transparent 1px)',
        backgroundSize: '100% 100%, 100% 100%, 32px 32px, 32px 32px'
      }}
    >
      {/* Ambient Nebulae */}
      <div className="nebula-yellow" />
      <div className="nebula-pink" />

      {/* Twinkling Star Field */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        {stars.map(st => (
          <div
            key={st.id}
            className={`star absolute ${st.size} rounded-full opacity-60 ${
              st.isPink
                ? 'bg-[#ff4b89] shadow-[0_0_8px_rgba(255,75,137,0.6)]'
                : 'bg-[#fee400] shadow-[0_0_8px_rgba(254,228,0,0.6)]'
            }`}
            style={{
              top: `${st.top}%`,
              left: `${st.left}%`,
              animationDuration: `${st.duration}s`,
              animationDelay: `${st.delay}s`
            }}
          />
        ))}
      </div>

      {/* TOP LEFT HUD: System Time & Core Sync */}
      <div className="absolute top-6 left-8 z-30 flex items-center gap-4">
        <div className={`px-3 py-1.5 rounded-lg border font-mono-code text-xs flex items-center gap-2 ${
          themeMode === 'light'
            ? 'bg-white/80 border-[#fee400]/40 text-[#131313] shadow-sm'
            : 'bg-[#201f1f]/60 border-[#fee400]/20 text-[#e5e2e1]'
        }`}>
          <span className="w-2 h-2 rounded-full bg-[#fee400] animate-ping" />
          <span className="font-bold tracking-wider text-[#fee400]">SYS_TIME</span>
          <span className="opacity-80">{currentTime || '00:00:00'}</span>
          <span className="text-[10px] opacity-50">:{millisec.toString().padStart(2, '0')}</span>
        </div>

        <div className={`px-3 py-1.5 rounded-lg border font-mono-code text-xs flex items-center gap-2 ${
          themeMode === 'light'
            ? 'bg-white/80 border-[#ff4b89]/30 text-[#131313]'
            : 'bg-[#201f1f]/60 border-[#ff4b89]/20 text-[#e5e2e1]'
        }`}>
          <Zap className="w-3.5 h-3.5 text-[#ff4b89]" />
          <span className="opacity-70 text-[11px]">SYNC</span>
          <span className="font-bold text-[#ff4b89]">{syncRate}%</span>
        </div>
      </div>

      {/* TOP RIGHT HUD: Quick Controls */}
      <div className="absolute top-6 right-8 z-30 flex items-center gap-2">
        <button
          onClick={handleDemoVoiceTalk}
          className={`px-3 py-1.5 rounded-lg border font-mono-code text-xs flex items-center gap-1.5 transition-all cursor-pointer ${
            isSpeaking
              ? 'bg-[#fee400] text-black font-bold border-[#fee400] shadow-[0_0_20px_rgba(254,228,0,0.6)] animate-pulse'
              : 'bg-white/90 dark:bg-[#201f1f]/80 border-slate-300 dark:border-[#4b4731] hover:border-[#fee400] text-slate-800 dark:text-[#e5e2e1]'
          }`}
          title="Test Voice Speech Expansion"
        >
          <Waves className={`w-3.5 h-3.5 ${isSpeaking ? 'text-black animate-spin' : 'text-[#fee400]'}`} />
          <span>TEST VOICE</span>
        </button>

        <button
          onClick={toggleListening}
          className={`px-3 py-1.5 rounded-lg border font-mono-code text-xs flex items-center gap-1.5 transition-all cursor-pointer ${
            isListening
              ? 'bg-[#fee400] text-black font-bold border-[#fee400] shadow-[0_0_20px_rgba(254,228,0,0.6)] animate-pulse'
              : 'bg-white/90 dark:bg-[#201f1f]/80 border-slate-300 dark:border-[#4b4731] hover:border-[#fee400] text-slate-800 dark:text-[#e5e2e1]'
          }`}
          title="Toggle Mic Voice Listening"
        >
          {isListening ? <Mic className="w-3.5 h-3.5 text-black" /> : <MicOff className="w-3.5 h-3.5 text-[#fee400]" />}
          <span>{isListening ? 'LISTENING' : 'VOICE MIC'}</span>
        </button>

        <button
          onClick={() => {
            playPulseSound(600, 'sine', 0.1);
            setThemeMode(prev => prev === 'light' ? 'dark' : 'light');
          }}
          className={`p-2 rounded-lg border transition-all cursor-pointer ${
            themeMode === 'light'
              ? 'bg-white/90 border-slate-300 hover:border-[#fee400] text-slate-700 shadow-sm'
              : 'bg-[#201f1f]/80 border-[#4b4731] hover:border-[#fee400] text-[#e5e2e1]'
          }`}
          title="Toggle UI Canvas Theme"
        >
          {themeMode === 'light' ? <Moon className="w-4 h-4 text-slate-800" /> : <Sun className="w-4 h-4 text-[#fee400]" />}
        </button>

        <button
          onClick={() => setIsAudioMuted(prev => !prev)}
          className={`p-2 rounded-lg border transition-all cursor-pointer ${
            isAudioMuted
              ? 'bg-red-500/10 border-red-500/40 text-red-400'
              : themeMode === 'light'
                ? 'bg-white/90 border-slate-300 hover:border-[#fee400] text-slate-800 shadow-sm'
                : 'bg-[#201f1f]/80 border-[#4b4731] hover:border-[#fee400] text-[#fee400]'
          }`}
          title={isAudioMuted ? 'Unmute Audio Pulse' : 'Mute Audio Pulse'}
        >
          {isAudioMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </button>

        <button
          onClick={() => {
            playPulseSound(520, 'triangle', 0.15);
            setIsDiagnosticsOpen(prev => !prev);
          }}
          className={`px-3 py-1.5 rounded-lg border font-mono-code text-xs flex items-center gap-1.5 transition-all cursor-pointer ${
            isDiagnosticsOpen
              ? 'bg-[#fee400] text-black font-bold border-[#fee400]'
              : themeMode === 'light'
                ? 'bg-white/90 border-slate-300 hover:border-[#fee400] text-slate-800 shadow-sm'
                : 'bg-[#201f1f]/80 border-[#4b4731] hover:border-[#fee400] text-[#e5e2e1]'
          }`}
        >
          <Sliders className="w-3.5 h-3.5 text-[#ff4b89]" />
          <span>PARAMS</span>
        </button>

        <button
          onClick={() => setIsTerminalOpen(prev => !prev)}
          className={`px-3.5 py-1.5 rounded-lg border font-mono-code text-xs flex items-center gap-2 transition-all cursor-pointer ${
            isTerminalOpen
              ? 'bg-[#ff4b89] text-white font-bold border-[#ff4b89] shadow-[0_0_15px_rgba(255,75,137,0.4)]'
              : 'bg-[#fee400] text-black font-bold border-[#fee400] hover:bg-[#ebd300] shadow-[0_0_15px_rgba(254,228,0,0.3)]'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>TERMINAL</span>
        </button>
      </div>

      {/* CENTRAL HOLOGRAPHIC CORE WITH DYNAMIC VOICE EXPANSION & GLOW */}
      <div className="holo-container z-10 pointer-events-none">
        {/* Animated Ripple Rings when Voice is Active */}
        {(isSpeaking || isListening) && (
          <>
            <div className="voice-ripple w-[240px] h-[240px]" style={{ animationDelay: '0s' }} />
            <div className="voice-ripple w-[360px] h-[360px]" style={{ animationDelay: '0.5s' }} />
            <div className="voice-ripple w-[480px] h-[480px]" style={{ animationDelay: '1s' }} />
          </>
        )}

        {/* Ring 1 - Yellow solid glow ring */}
        <div
          className={`holo-ring holo-ring-1 pointer-events-auto cursor-pointer transition-all duration-700 ease-out ${
            isSpeaking
              ? 'scale-115 border-[#fee400] shadow-[0_0_50px_#fee400,inset_0_0_40px_#fee400]'
              : isListening
                ? 'scale-105 border-[#fee400] shadow-[0_0_30px_#fee400]'
                : ''
          }`}
          onClick={handleCoreClick}
          style={{
            animationDuration: `${20 / coreSpeed}s`,
            animationPlayState: isListening ? 'paused' : 'running'
          }}
        >
          <div className="particle" style={{ top: 0, left: '50%' }} />
          <div className="particle" style={{ bottom: 0, left: '50%' }} />
        </div>

        {/* Ring 2 - Dashed ring */}
        <div
          className={`holo-ring holo-ring-2 pointer-events-auto cursor-pointer transition-all duration-700 ease-out ${
            isSpeaking
              ? 'scale-120 border-[#fee400] shadow-[0_0_50px_rgba(254,228,0,0.8)]'
              : isListening
                ? 'scale-105 border-[#fee400]/80'
                : ''
          }`}
          onClick={handleCoreClick}
          style={{
            animationDuration: `${30 / coreSpeed}s`,
            animationPlayState: isListening ? 'paused' : 'running'
          }}
        >
          <div className="particle" style={{ top: '50%', left: 0 }} />
          <div className="particle" style={{ top: '50%', right: 0 }} />
        </div>

        {/* Ring 3 - Outer gradient ring */}
        <div
          className={`holo-ring holo-ring-3 pointer-events-auto cursor-pointer transition-all duration-700 ease-out ${
            isSpeaking ? 'scale-115 border-[#fee400]' : ''
          }`}
          onClick={handleCoreClick}
          style={{
            animationDuration: `${45 / coreSpeed}s`,
            animationPlayState: isListening ? 'paused' : 'running'
          }}
        >
          <div className="particle" style={{ top: '25%', left: '25%' }} />
          <div className="particle" style={{ bottom: '25%', right: '25%' }} />
        </div>

        {/* Visual Audio Wave Spectrum Bars around Core when speaking */}
        {isSpeaking && (
          <div className="absolute w-[210px] h-[210px] flex items-center justify-center pointer-events-none">
            {Array.from({ length: 24 }).map((_, i) => (
              <div
                key={i}
                className="absolute w-1 rounded-full bg-gradient-to-t from-[#fee400] to-[#fff480] animate-pulse"
                style={{
                  height: `${16 + Math.sin(i * 0.8) * 32 + Math.random() * 20}px`,
                  transform: `rotate(${i * 15}deg) translateY(-100px)`,
                  animationDuration: `${0.35 + (i % 5) * 0.15}s`
                }}
              />
            ))}
          </div>
        )}

        {/* Core Pulsing Sphere - Smooth Expansion Container */}
        <div
          className={`transition-all duration-700 ease-out flex items-center justify-center ${
            isSpeaking
              ? 'scale-125'
              : isListening
                ? 'scale-100'
                : 'scale-100'
          }`}
        >
          <div
            className={`holo-core pointer-events-auto group relative transition-all duration-700 ${
              isSpeaking
                ? 'voice-speaking'
                : isListening
                  ? 'voice-listening'
                  : ''
            }`}
            onClick={handleCoreClick}
            title={isSpeaking ? 'AI Speaking - Click to stop voice' : 'Click to trigger voice talk test'}
          >
            <div className={`absolute -inset-3 rounded-full border border-[#fee400]/40 pointer-events-none transition-all duration-700 ${
              isSpeaking ? 'animate-ping border-[#fee400] opacity-80 duration-300' : 'opacity-20'
            }`} />
          </div>
        </div>

        {/* Display Typography Title & Speech Status Badge */}
        <div
          className="absolute text-center mt-64 pointer-events-auto cursor-pointer group flex flex-col items-center"
          onClick={handleCoreClick}
        >
          <h1 className={`font-space text-5xl md:text-6xl font-bold mb-2 tracking-tighter transition-all duration-300 ${
            isSpeaking
              ? 'text-[#fee400] scale-105 drop-shadow-[0_0_25px_rgba(254,228,0,0.9)]'
              : isListening
                ? 'text-[#fee400] drop-shadow-[0_0_20px_rgba(254,228,0,0.8)]'
                : 'text-[#fee400] opacity-90 drop-shadow-[0_0_16px_rgba(254,228,0,0.6)] group-hover:scale-105'
          }`}>
            ARISU_v1.0
          </h1>

          {/* Dynamic Voice Status Badge */}
          {isSpeaking ? (
            <div className="mt-2 px-4 py-1.5 rounded-full bg-[#fee400]/25 border border-[#fee400] text-[#fee400] font-mono-code text-xs font-bold tracking-widest flex items-center gap-2 animate-pulse shadow-[0_0_25px_rgba(254,228,0,0.6)]">
              <Waves className="w-4 h-4 text-[#fee400] animate-spin" />
              <span>🔊 ARISU VOICE TRANSMITTING...</span>
            </div>
          ) : isListening ? (
            <div className="mt-2 px-4 py-1.5 rounded-full bg-[#fee400]/20 border border-[#fee400] text-[#fee400] font-mono-code text-xs font-bold tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(254,228,0,0.5)]">
              <Mic className="w-4 h-4 text-[#fee400]" />
              <span>🎙️ NEURAL SUBNET LISTENING...</span>
            </div>
          ) : isThinking ? (
            <div className="mt-2 px-4 py-1.5 rounded-full bg-[#fee400]/15 border border-[#fee400]/50 text-[#fee400] font-mono-code text-xs tracking-widest flex items-center gap-2 animate-pulse">
              <Sparkles className="w-3.5 h-3.5 text-[#fee400] animate-spin" />
              <span>PROCESSING NEURAL CORE...</span>
            </div>
          ) : (
            <h2 className="font-mono-code text-xs md:text-sm text-[#cec7aa] tracking-[0.3em] uppercase opacity-70 group-hover:text-[#fee400] transition-colors">
              NEURAL CORE ACTIVE
            </h2>
          )}
        </div>
      </div>

      {/* BOTTOM LEFT HUD: Telemetry Metrics */}
      <div className="absolute bottom-8 left-8 z-30 hidden md:flex flex-col gap-2 font-mono-code text-[11px] opacity-80 hover:opacity-100 transition-opacity">
        <div className={`p-3 rounded-lg border flex items-center gap-3 ${
          themeMode === 'light'
            ? 'bg-white/80 border-slate-200 text-slate-700 shadow-sm'
            : 'bg-[#201f1f]/60 border-[#4b4731] text-[#cec7aa]'
        }`}>
          <Activity className="w-4 h-4 text-[#fee400]" />
          <div>
            <div className="text-[10px] text-slate-400">PULSE RATE</div>
            <div className="font-bold text-[#fee400]">{corePulseRate} BPM</div>
          </div>
          <div className="w-px h-6 bg-slate-300 dark:bg-slate-700 mx-1" />
          <Cpu className="w-4 h-4 text-[#ff4b89]" />
          <div>
            <div className="text-[10px] text-slate-400">FRAME RATE</div>
            <div className="font-bold text-[#ff4b89]">{fps} FPS</div>
          </div>
          <div className="w-px h-6 bg-slate-300 dark:bg-slate-700 mx-1" />
          <Waves className="w-4 h-4 text-[#fee400]" />
          <div>
            <div className="text-[10px] text-slate-400">VOICE MODULE</div>
            <div className="font-bold text-[#fee400]">{isSpeaking ? 'TRANSMITTING' : isListening ? 'LISTENING' : 'STANDBY'}</div>
          </div>
        </div>
      </div>

      {/* DIAGNOSTICS & PARAMETERS SLIDE-OUT PANEL */}
      {isDiagnosticsOpen && (
        <div className={`absolute top-20 right-8 z-40 w-80 p-5 rounded-xl border font-mono-code text-xs shadow-2xl backdrop-blur-xl transition-all animate-in fade-in slide-in-from-top-4 ${
          themeMode === 'light'
            ? 'bg-white/95 border-[#fee400] text-slate-800 shadow-yellow-500/10'
            : 'bg-[#1c1b1b]/95 border-[#fee400]/40 text-[#e5e2e1]'
        }`}>
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-2 font-bold text-[#fee400]">
              <Sliders className="w-4 h-4 text-[#ff4b89]" />
              <span>CORE PARAMETERS</span>
            </div>
            <button
              onClick={() => setIsDiagnosticsOpen(false)}
              className="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded text-slate-500 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-4">
            {/* Voice Synthesis Toggle */}
            <div className="flex items-center justify-between p-2 rounded bg-slate-100 dark:bg-[#252525]">
              <span className="text-slate-600 dark:text-slate-300 text-[11px]">VOICE SYNTHESIS (TTS)</span>
              <button
                onClick={() => setIsVoiceEnabled(prev => !prev)}
                className={`px-2.5 py-1 rounded text-[10px] font-bold cursor-pointer ${
                  isVoiceEnabled ? 'bg-[#fee400] text-black' : 'bg-slate-300 dark:bg-slate-700 text-slate-600'
                }`}
              >
                {isVoiceEnabled ? 'ENABLED' : 'DISABLED'}
              </button>
            </div>

            {/* Core Rotation Speed */}
            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-500 dark:text-slate-400">ROTATION SPEED</span>
                <span className="text-[#fee400] font-bold">{coreSpeed.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="3"
                step="0.1"
                value={coreSpeed}
                onChange={e => setCoreSpeed(parseFloat(e.target.value))}
                className="w-full accent-[#fee400] cursor-pointer"
              />
            </div>

            {/* Particle Density */}
            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-slate-500 dark:text-slate-400">STAR FIELD DENSITY</span>
                <span className="text-[#ff4b89] font-bold">{starCount} UNITS</span>
              </div>
              <input
                type="range"
                min="10"
                max="80"
                step="5"
                value={starCount}
                onChange={e => setStarCount(parseInt(e.target.value))}
                className="w-full accent-[#ff4b89] cursor-pointer"
              />
            </div>

            {/* Actions */}
            <div className="pt-2 flex gap-2">
              <button
                onClick={handleDemoVoiceTalk}
                className="flex-1 py-1.5 px-2 bg-[#fee400] text-black font-bold rounded text-[11px] flex items-center justify-center gap-1 cursor-pointer"
              >
                <Waves className="w-3 h-3" />
                <span>SPEAK TEST</span>
              </button>
              <button
                onClick={() => {
                  setCoreSpeed(1);
                  setStarCount(35);
                  playPulseSound(300, 'sine', 0.1);
                }}
                className="py-1.5 px-3 bg-slate-100 dark:bg-[#2a2a2a] hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-[11px] flex items-center justify-center gap-1 cursor-pointer"
              >
                <RotateCcw className="w-3 h-3" />
                <span>RESET</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ARISU NEURAL AI CHAT TERMINAL OVERLAY */}
      {isTerminalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-200">
          <div className={`w-full max-w-2xl h-[580px] rounded-2xl border flex flex-col shadow-2xl overflow-hidden font-mono-code ${
            themeMode === 'light'
              ? 'bg-white border-[#fee400] text-slate-800 shadow-yellow-500/20'
              : 'bg-[#1c1b1b] border-[#fee400]/50 text-[#e5e2e1]'
          }`}>
            {/* Header */}
            <div className="px-5 py-4 border-b border-slate-200 dark:border-[#353534] bg-slate-50/50 dark:bg-[#201f1f]/80 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full border border-[#fee400] flex items-center justify-center bg-[#2a2a2a] shrink-0 text-[#fee400]">
                  <Cpu className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-sm font-bold text-[#fee400] tracking-wider flex items-center gap-2">
                    <span>ARISU_v1.0 NEURAL TERMINAL</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#ff4b89]/20 text-[#ff4b89] font-normal">
                      ONLINE
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Direct Subnet Interface • Gemini Powered
                  </div>
                </div>
              </div>

              <button
                onClick={() => setIsTerminalOpen(false)}
                className="p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-500 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Presets */}
            <div className="px-4 py-2 border-b border-slate-200 dark:border-[#2a2a2a] bg-slate-100/50 dark:bg-[#131313]/50 flex gap-2 overflow-x-auto text-[10px]">
              {[
                'Run System Diagnostic',
                'Analyze Core Sync Rate',
                'ARISU, introduce yourself',
                'Check Memory Allocation'
              ].map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(preset)}
                  className="px-2.5 py-1 rounded bg-slate-200 dark:bg-[#201f1f] hover:bg-[#fee400] hover:text-black dark:hover:bg-[#fee400] dark:hover:text-black transition-colors whitespace-nowrap border border-slate-300 dark:border-slate-800 cursor-pointer"
                >
                  {preset}
                </button>
              ))}
            </div>

            {/* Chat Body */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4 text-xs">
              {chatHistory.map(msg => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${
                    msg.sender === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1 text-[10px] text-slate-400">
                    <span>{msg.sender === 'user' ? 'OPERATOR' : 'ARISU_v1.0'}</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                  </div>
                  
                  {/* Thought Block Component */}
                  {msg.thought && (
                    <details className="mb-2 w-full max-w-[85%] border border-[#fee400]/30 rounded-lg bg-black/20 text-[10px] text-[#fee400]">
                      <summary className="px-3 py-1.5 cursor-pointer font-bold tracking-wider hover:bg-black/40">
                        INTERNAL CORE ANALYSIS
                      </summary>
                      <div className="p-3 border-t border-[#fee400]/30 whitespace-pre-wrap font-mono">
                        {msg.thought}
                      </div>
                    </details>
                  )}

                  <div
                    className={`max-w-[85%] p-3 rounded-xl whitespace-pre-wrap leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-[#fee400] text-black font-medium rounded-tr-none'
                        : themeMode === 'light'
                          ? 'bg-slate-100 text-slate-800 border border-slate-200 rounded-tl-none'
                          : 'bg-[#201f1f] text-[#e5e2e1] border border-[#353534] rounded-tl-none'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}

              {isThinking && (
                <div className="flex items-center gap-2 text-[#fee400] text-xs">
                  <span className="w-2 h-2 rounded-full bg-[#fee400] animate-ping" />
                  <span>Processing neural query through ARISU core...</span>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            {/* Chat Input */}
            <form
              onSubmit={e => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="p-3 border-t border-slate-200 dark:border-[#353534] bg-slate-50 dark:bg-[#131313] flex gap-2"
            >
              <button
                type="button"
                onClick={toggleListening}
                className={`p-2 rounded-lg border transition-colors cursor-pointer ${
                  isListening
                    ? 'bg-[#ff4b89] text-white border-[#ff4b89] animate-pulse'
                    : 'bg-slate-200 dark:bg-[#201f1f] text-slate-700 dark:text-[#e5e2e1] border-slate-300 dark:border-slate-700 hover:border-[#fee400]'
                }`}
                title="Voice Dictation"
              >
                <Mic className="w-4 h-4" />
              </button>
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                placeholder="Enter command or question for ARISU..."
                className={`flex-1 px-3 py-2 text-xs rounded-lg border outline-none focus:border-[#fee400] ${
                  themeMode === 'light'
                    ? 'bg-white border-slate-300 text-slate-900'
                    : 'bg-[#201f1f] border-slate-700 text-[#e5e2e1]'
                }`}
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || isThinking}
                className="px-4 py-2 bg-[#fee400] hover:bg-[#ebd300] text-black font-bold text-xs rounded-lg flex items-center gap-1.5 transition-colors disabled:opacity-50 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                <span>SEND</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
