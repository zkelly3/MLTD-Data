// vue.config.js

/**
 * @type {import('@vue/cli-service').ProjectOptions}
 */
module.exports = {
  runtimeCompiler: true,
  devServer: {
      proxy: {
          '/api': { target: 'http://mltd.csie.org' },
          '/static/images': { target: 'http://mltd.csie.org' },
      },
  },
}
