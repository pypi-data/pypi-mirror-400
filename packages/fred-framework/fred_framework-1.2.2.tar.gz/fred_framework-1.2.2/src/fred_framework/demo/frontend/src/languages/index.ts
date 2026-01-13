import { createI18n } from "vue-i18n";
import { getBrowserLang } from "@/utils";
import { watch } from "vue";
import zh from "./modules/zh";
import en from "./modules/en";

const defaultLocale = localStorage.getItem("locale") || getBrowserLang();
localStorage.setItem("locale", defaultLocale);

const i18n = createI18n({
  // Use Composition API, Set to false
  allowComposition: true,
  legacy: false,
  locale: defaultLocale,
  messages: {
    zh,
    en
  },
  fallbackLocale: "zh", // 兜底语言
  silentTranslationWarn: true, // 在生产环境关闭警告
  silentFallbackWarn: true
});

// 响应式监听 locale 切换，自动同步 localStorage
watch(
  () => i18n.global.locale.value,
  val => {
    localStorage.setItem("locale", val);
  }
);

export default i18n;
