// 动画和语音资源映射表

const ASSETS_BASE = 'assets';

const ANIMATIONS = {
  relax:    `${ASSETS_BASE}/animations/麦哲伦-默认-基建-Relax-x1.webm`,
  interact: `${ASSETS_BASE}/animations/麦哲伦-默认-基建-Interact-x1.webm`,
  move:     `${ASSETS_BASE}/animations/麦哲伦-默认-基建-Move-x1.webm`,
  sit:      `${ASSETS_BASE}/animations/麦哲伦-默认-基建-Sit-x1.webm`,
  sleep:    `${ASSETS_BASE}/animations/麦哲伦-默认-基建-Sleep-x1.webm`,
  idle:     `${ASSETS_BASE}/animations/麦哲伦-默认-正面-Idle-x1.webm`,
  start:    `${ASSETS_BASE}/animations/麦哲伦-默认-正面-Start-x1.webm`,
  skill:    `${ASSETS_BASE}/animations/麦哲伦-默认-正面-Skill-x1.webm`,
  attack:   `${ASSETS_BASE}/animations/麦哲伦-默认-正面-Attack-x1.webm`,
  die:      `${ASSETS_BASE}/animations/麦哲伦-默认-正面-Die-x1.webm`,
  backIdle: `${ASSETS_BASE}/animations/麦哲伦-默认-背面-Idle-x1.webm`,
  backStart:`${ASSETS_BASE}/animations/麦哲伦-默认-背面-Start-x1.webm`,
  backSkill:`${ASSETS_BASE}/animations/麦哲伦-默认-背面-Skill-x1.webm`,
  backAttack:`${ASSETS_BASE}/animations/麦哲伦-默认-背面-Attack-x1.webm`,
};

const ANIM_LOOP = {
  relax: true, move: true, idle: true, backIdle: true, sleep: true, sit: true,
  interact: false, start: false, skill: false, attack: false, die: false,
  backStart: false, backSkill: false, backAttack: false,
};

// 语音文件映射
const VOICES = {
  poke:     ['voices/戳一下.wav'],
  select:   ['voices/选中干员1.wav', 'voices/选中干员2.wav'],
  greet:    ['voices/问候.wav'],
  talk:     ['voices/交谈1.wav', 'voices/交谈2.wav', 'voices/交谈3.wav'],
  idle:     ['voices/闲置.wav'],
  trustTap: ['voices/信赖触摸.wav'],
  startup:  ['voices/干员报到.wav'],
  assistant:['voices/任命助理.wav'],
  battle:   ['voices/作战中1.wav', 'voices/作战中2.wav', 'voices/作战中3.wav', 'voices/作战中4.wav'],
  deploy:   ['voices/部署1.wav', 'voices/部署2.wav'],
  actionStart: ['voices/行动开始.wav'],
  actionGo: ['voices/行动出发.wav'],
  promote:  ['voices/晋升后交谈1.wav', 'voices/晋升后交谈2.wav'],
  trust:    ['voices/信赖提升后交谈1.wav', 'voices/信赖提升后交谈2.wav', 'voices/信赖提升后交谈3.wav'],
  elite:    ['voices/精英化晋升1.wav', 'voices/精英化晋升2.wav'],
  facility: ['voices/进驻设施.wav'],
  squad:    ['voices/编入队伍.wav'],
  captain:  ['voices/任命队长.wav'],
  fail:     ['voices/行动失败.wav'],
  record:   ['voices/观看作战记录.wav'],
  bday:     ['voices/生日.wav'],
  newyear:  ['voices/新年祝福.wav'],
  anni:     ['voices/周年庆典.wav'],
  title:    ['voices/标题.wav'],
  highDiff: ['voices/完成高难行动.wav'],
  non3star: ['voices/非3星结束行动.wav'],
};

function voicePath(name) {
  return `${ASSETS_BASE}/${name}`;
}

// 交互 -> 语音类别（更丰富的映射）
const BEHAVIOR_VOICES = {
  // 单击：戳、选中、问候
  click:       ['poke', 'select', 'select', 'greet', 'trustTap'],
  // 双击：作战技能
  doubleClick: ['battle', 'deploy', 'actionStart'],
  // 出场
  startup:     ['startup'],
  // 30秒无操作 → 坐下 + 闲置台词
  sitDown:     ['idle', 'trustTap', 'record'],
  // 2分钟无操作 → 随机交谈
  idleChat:    ['talk', 'assistant', 'promote', 'trust', 'facility'],
  // 自主小走动 → 简短台词
  autoWalk:    ['actionGo', 'squad', 'captain', 'deploy'],
  // 轻戳动作（自主小动作，通常不说话）
  fidget:      ['poke', 'select'],
  // 睡觉
  goSleep:     ['idle'],
  // 右键"说句话"
  menuTalk:    ['talk', 'assistant', 'promote', 'trustTap', 'facility', 'elite'],
  // 右键"无人机"
  menuSkill:   ['battle', 'actionStart', 'deploy'],
  // 右键"走一走"
  menuWalk:    ['actionGo', 'squad', 'captain'],
  // 右键"坐下"
  menuSit:     ['trustTap', 'record'],
  // 右键"睡觉"
  menuSleep:   ['idle'],
};

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function getRandomVoice(behaviorKey) {
  const voiceKeys = BEHAVIOR_VOICES[behaviorKey];
  if (!voiceKeys) return null;
  const key = pickRandom(voiceKeys);
  const files = VOICES[key];
  return files ? voicePath(pickRandom(files)) : null;
}

// 语音文字（气泡）
const VOICE_TEXT = {
  '戳一下': '唉？',
  '选中干员1': '嗯！',
  '选中干员2': '需要我的技术了吗？',
  '问候': '有什么事吗？',
  '交谈1': '其实我知道博士很久了哦！梅尔和缪缪她们都和我说过博士你的！我还给你带了小礼物哦！给！',
  '交谈2': '这个是大帝的挂坠，就是企鹅物流的那个大帝呀，真的好可爱，每次过去都会摸上好久！',
  '交谈3': '伊芙芙最近好点了吗，在我上一次离开莱茵生命的时候，她的状态有点糟糕，真的好担心……',
  '闲置': '博士？博士不可以！如果睡着的话，会没命的！',
  '信赖触摸': '走嘛走嘛，溜冰没那么可怕的，有我在呢。',
  '干员报到': '莱茵生命科考专员麦哲伦，发现了一艘神秘的科研船？哇哇哇，你是罗德岛的博士吧，要不要加入我的探险队呢？',
  '任命助理': '在下次探险之前我会一直待在你身边的，博士。有需要我的地方，请别顾虑什么，大胆地派遣我吧。',
  '作战中1': '目标就位了吗？好，无人机激活！',
  '作战中2': '就是现在！雪盲可是很可怕的哦！',
  '作战中3': '3……2……1！',
  '作战中4': '花啊！绽放吧！',
  '部署1': '开始工作！',
  '部署2': '设备运行良好！',
  '行动开始': '无人机调试完毕，随时可以升空。',
  '行动出发': '还得调试下设备……好了！',
  '晋升后交谈1': '梅尔最近有造什么新东西吗，我好久没有做过新的装备，也该和她一起做些研究啦。',
  '晋升后交谈2': '哼哼哼，事先说好，我可是很强的，可不要被吓到哦！',
  '信赖提升后交谈1': '极北吗？那是个冰冷又残酷的梦境，但是啊，就是在那样的地方，埋藏着我的梦想。',
  '信赖提升后交谈2': '小小园丁，小小花，开在屋檐下，没人照料它……这是伊芙芙以前最爱的读本。',
  '信赖提升后交谈3': '极北啊……那是个既神秘又美丽的地方。博士，和我一起去吧，好吗？',
  '精英化晋升1': '升级完成！现在设备的反应速度，要比之前快上一倍哦。',
  '精英化晋升2': '如果博士想看看我研究的成果，我也必须要展现一下我的实力了！哼哼哼，事先说好，我可是很强的，可不要被吓到哦！',
  '进驻设施': '唔？居，居然有地暖！啊~太好了~',
  '编入队伍': '勘探和支援就交给我吧！',
  '任命队长': '各位，要注意保持联络哦，哔哔！',
  '行动失败': '被包抄了？是我的失误……',
  '观看作战记录': '效率提升了呢。',
  '完成高难行动': '当心啊，那里是扫描盲区！呃，已经清空了？不愧是博士，真可靠呢。',
  '非3星结束行动': '附近还有人，要追击吗？',
};

function getVoiceText(filePath) {
  const match = filePath.match(/([^/]+)\.wav$/);
  if (!match) return '';
  return VOICE_TEXT[match[1]] || '';
}
