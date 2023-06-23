
export const useRules = () => {
  return ValidationRules
}

class ValidationRules {
  public static required(v: string) {
    return !!v || "Required."
  }


  public static maxLength(n: number) {
    return (v: string) => {
      return (v && v.length <= n) || `Must be less than ${n} characters.`
    }
  }
  public static minLength(n: number) {
    return (v: string) => {
      return (v && v.length >= n) || `Must be more than ${n} characters.`
    }
  }

  public static max(n: number) {
    return (v: string | number) => {
      const num = typeof v === "string" ? parseInt(v) : v
      return (!isNaN(num) && num <= n) || `Must be less than ${n}.`
    }
  }

  public static min(n: number) {
    return (v: string | number) => {
      const num = typeof v === "string" ? parseInt(v) : v
      return (!isNaN(num) && num >= n) || `Must be more than ${n}.`
    }
  }
}