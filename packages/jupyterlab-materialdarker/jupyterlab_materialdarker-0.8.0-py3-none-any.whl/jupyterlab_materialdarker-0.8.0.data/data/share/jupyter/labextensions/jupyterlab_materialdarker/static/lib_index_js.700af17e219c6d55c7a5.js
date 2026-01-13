"use strict";
(self["webpackChunkjupyterlab_materialdarker"] = self["webpackChunkjupyterlab_materialdarker"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js"
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);

/**
 * Initialization data for the jupyterlab_materialdarker extension.
 */
const plugin = {
    id: 'jupyterlab_materialdarker:plugin',
    description: 'The Material Darker theme for JupyterLab.',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.IThemeManager],
    activate: (app, manager) => {
        console.log('JupyterLab extension jupyterlab_materialdarker is activated!');
        const style = '@oriolmirosa/jupyterlab_materialdarker/index.css';
        manager.register({
            name: 'Material Darker',
            isLight: false,
            load: () => manager.loadCSS(style),
            unload: () => Promise.resolve(undefined)
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }

}]);
//# sourceMappingURL=lib_index_js.700af17e219c6d55c7a5.js.map