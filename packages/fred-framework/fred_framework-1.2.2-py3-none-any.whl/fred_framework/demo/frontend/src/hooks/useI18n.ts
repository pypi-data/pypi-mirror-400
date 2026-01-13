import { useI18n as useVueI18n } from "vue-i18n";

/**
 * 国际化 hooks
 * 提供便捷的国际化方法
 */
export const useI18n = () => {
  const { t, locale, messages } = useVueI18n();

  /**
   * 翻译函数
   * @param key 翻译 key
   * @param params 参数对象
   * @returns 翻译后的文本
   */
  const translate = (key: string, params?: Record<string, any>): string => {
    return t(key, params);
  };

  /**
   * 设置语言
   * @param lang 语言代码
   */
  const setLocale = (lang: string) => {
    locale.value = lang;
  };

  /**
   * 获取当前语言
   */
  const getLocale = () => {
    return locale.value;
  };

  /**
   * 获取所有支持的语言
   */
  const getSupportedLocales = () => {
    return Object.keys(messages.value);
  };

  return {
    t: translate,
    locale,
    messages,
    setLocale,
    getLocale,
    getSupportedLocales,
    translate
  };
};
