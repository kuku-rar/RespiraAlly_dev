/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from "react";

const AccessibilityContext = createContext({});

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error(
      "useAccessibility must be used within AccessibilityProvider"
    );
  }
  return context;
};

export const AccessibilityProvider = ({ children }) => {
  // 視覺無障礙狀態
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [isLargeText, setIsLargeText] = useState(false);

  // 語音無障礙狀態
  const [enableVoice, setEnableVoice] = useState(false);
  const [voiceRate, setVoiceRate] = useState(0.9);
  const [voiceVolume, setVoiceVolume] = useState(1);

  // 載入儲存的無障礙設定
  useEffect(() => {
    const savedHighContrast =
      localStorage.getItem("accessibility.highContrast") === "true";
    const savedLargeText =
      localStorage.getItem("accessibility.largeText") === "true";
    const savedVoice = localStorage.getItem("accessibility.voice") === "true";
    const savedVoiceRate =
      parseFloat(localStorage.getItem("accessibility.voiceRate")) || 0.9;
    const savedVoiceVolume =
      parseFloat(localStorage.getItem("accessibility.voiceVolume")) || 1;

    setIsHighContrast(savedHighContrast);
    setIsLargeText(savedLargeText);
    setEnableVoice(savedVoice);
    setVoiceRate(savedVoiceRate);
    setVoiceVolume(savedVoiceVolume);

    // 應用視覺設定到 DOM
    document.documentElement.setAttribute(
      "data-contrast",
      savedHighContrast ? "high" : "normal"
    );
    document.documentElement.setAttribute(
      "data-text-size",
      savedLargeText ? "large" : "normal"
    );
  }, []);

  // 切換高對比度
  const toggleHighContrast = () => {
    const newValue = !isHighContrast;
    setIsHighContrast(newValue);
    localStorage.setItem("accessibility.highContrast", String(newValue));
    document.documentElement.setAttribute(
      "data-contrast",
      newValue ? "high" : "normal"
    );
  };

  // 切換大字體
  const toggleLargeText = () => {
    const newValue = !isLargeText;
    setIsLargeText(newValue);
    localStorage.setItem("accessibility.largeText", String(newValue));
    document.documentElement.setAttribute(
      "data-text-size",
      newValue ? "large" : "normal"
    );
  };

  // 切換語音播報
  const toggleVoice = () => {
    const newValue = !enableVoice;
    setEnableVoice(newValue);
    localStorage.setItem("accessibility.voice", String(newValue));
  };

  // 設定語音速度
  const setVoiceSettings = (rate, volume) => {
    if (rate !== undefined) {
      setVoiceRate(rate);
      localStorage.setItem("accessibility.voiceRate", String(rate));
    }
    if (volume !== undefined) {
      setVoiceVolume(volume);
      localStorage.setItem("accessibility.voiceVolume", String(volume));
    }
  };

  // 語音播報功能
  const speak = (text, options = {}) => {
    if (!enableVoice || !window.speechSynthesis || !text) return;

    // 停止當前播報
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = options.lang || "zh-TW";
    utterance.rate = options.rate || voiceRate;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || voiceVolume;

    // 錯誤處理
    utterance.onerror = (event) => {
      console.warn("語音播報錯誤:", event.error);
    };

    window.speechSynthesis.speak(utterance);
  };

  // 停止語音播報
  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  };

  // 語音播報狀態檢查
  const isSpeaking = () => {
    return window.speechSynthesis ? window.speechSynthesis.speaking : false;
  };

  const value = {
    // 視覺無障礙
    isHighContrast,
    isLargeText,
    toggleHighContrast,
    toggleLargeText,

    // 語音無障礙
    enableVoice,
    voiceRate,
    voiceVolume,
    toggleVoice,
    setVoiceSettings,
    speak,
    stopSpeaking,
    isSpeaking,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};
