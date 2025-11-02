// 清理瀏覽器緩存的腳本
console.log("🧹 清理瀏覽器緩存...");

// 清理 localStorage
if (typeof localStorage !== "undefined") {
  localStorage.clear();
  console.log("✅ 清理 localStorage");
}

// 清理 sessionStorage
if (typeof sessionStorage !== "undefined") {
  sessionStorage.clear();
  console.log("✅ 清理 sessionStorage");
}

// 清理任何 LIFF 相關的全域變數
if (typeof window !== "undefined") {
  delete window.liff;
  window.liff = null;
  console.log("✅ 清理 LIFF 全域變數");
}

console.log("🎉 緩存清理完成！");
