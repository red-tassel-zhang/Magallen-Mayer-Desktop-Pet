// 主应用入口

(function () {
  'use strict';

  const canvas = document.getElementById('pet-canvas');

  // 初始化
  PetPlayer.init(canvas);
  Interactions.init();

  // 响应窗口 resize
  window.addEventListener('resize', () => PetPlayer.resize());

  // 主渲染循环 —— 持续把视频帧绘制到 Canvas
  function render() {
    PetPlayer.render();
    requestAnimationFrame(render);
  }

  requestAnimationFrame(render);

  // 启动序列
  Interactions.startup();
})();
