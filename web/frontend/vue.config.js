// vue.config.js

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
module.exports = {
  runtimeCompiler: true,
  devServer: {
      proxy: {
          '/api': { target: 'https://mltd.csie.org' },
          '/static/images': { target: 'https://mltd.csie.org' },
      },
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization"
      },
  },
}
