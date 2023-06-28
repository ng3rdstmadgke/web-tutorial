export const useRules = () => {
  return ValidationRules
}

class ValidationRules {
  // 必須入力のバリデーション
  public static required(v: string) {
    return !!v || "Required."
  }

  // 文字列長の最大値のバリデーション
  public static maxLength(n: number) {
    return (v: string) => {
      return (v && v.length <= n) || `Must be less than ${n} characters.`
    }
  }

  // 文字列長の最小値のバリデーション
  public static minLength(n: number) {
    return (v: string) => {
      return (v && v.length >= n) || `Must be more than ${n} characters.`
    }
  }

  // 数値の最大値のバリデーション
  public static max(n: number) {
    return (v: string | number) => {
      const num = typeof v === "string" ? parseInt(v) : v
      return (!isNaN(num) && num <= n) || `Must be less than ${n}.`
    }
  }

  // 数値の最小値のバリデーション
  public static min(n: number) {
    return (v: string | number) => {
      const num = typeof v === "string" ? parseInt(v) : v
      return (!isNaN(num) && num >= n) || `Must be more than ${n}.`
    }
  }
}
