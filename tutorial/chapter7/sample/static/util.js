window.CookieUtil = {
  getCookie: function(key) {
    let obj = Object.fromEntries(
      document.cookie
        .split(";")
        .map((e) => {
          return e.trim()
            .split("=")
            .map((k) => {
              return decodeURIComponent(k);
            });
        })
    );
    return obj[key];
  },
  setCookie: function(key, value) {
    document.cookie = encodeURIComponent(key) + "=" + encodeURIComponent(value);
  }
}