<template>
  <div class="tl-shell">
    <!-- Left Sidebar -->
    <aside class="tl-sidebar">
      <div class="tl-sidebar-header">
        <h2 class="tl-title">精选模板</h2>
        <div class="tl-filter">
          <button
            v-for="cat in categories"
            :key="cat.id"
            class="tl-filter-btn"
            :class="{ on: activeCategory === cat.id }"
            @click="activeCategory = cat.id"
          >{{ cat.label }}</button>
        </div>
      </div>

      <div class="tl-list">
        <button
          v-for="t in filteredTemplates"
          :key="t.id"
          class="tl-card"
          :class="{ picked: activeId === t.id }"
          @mouseenter="activeId = t.id"
          @click="activeId = t.id"
        >
          <div class="tl-card-visual">
            <div class="tl-card-thumb" :style="{ '--accent': t.accentColor }" v-html="getThumbHtml(t.id, t.accentColor)"></div>
          </div>
          <div class="tl-card-meta">
            <div class="tl-card-name">{{ t.name }}</div>
            <div class="tl-card-desc">{{ t.description }}</div>
            <div class="tl-card-tags">
              <span v-for="tag in t.tags" :key="tag" class="tl-tag">{{ tag }}</span>
            </div>
          </div>
        </button>
      </div>
    </aside>

    <!-- Right Preview -->
    <main class="tl-preview">
      <div class="tl-preview-header">
        <span class="tl-preview-name">{{ activeTemplate?.name }}</span>
        <span class="tl-preview-hint">Hover 左侧切换预览</span>
      </div>
      <div class="tl-paper-wrap">
        <div class="tl-paper" :key="activeId">
          <div class="tl-resume" v-html="activeTemplate?.htmlContent"></div>
        </div>
      </div>
      <div class="tl-preview-actions">
        <button class="tl-use-btn" @click="useActive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          使用此模板
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  accentColor: string;
  htmlContent: string;
}

const categories = [
  { id: 'all', label: '全部' },
  { id: 'professional', label: '商务专业' },
  { id: 'creative', label: '创意设计' },
  { id: 'minimal', label: '简约现代' },
];

const emit = defineEmits<{
  selectTemplate: [templateId: string];
}>();

// ═══ Template HTML generators ═══

const getThumbHtml = (id: string, accent: string): string => {
  const map: Record<string, string> = {
    'minimal-clean': `<div class="rt-thumb" style="background:#fff;color:#111;padding:12px 10px;text-align:center;font-family:sans-serif;"><div style="font-size:11px;font-weight:800;letter-spacing:1px;margin-bottom:6px;">张思文</div><div style="font-size:5px;color:#666;margin-bottom:2px;">产品经理 · 北京 · 30K-40K</div><div style="font-size:5px;color:#666;margin-bottom:6px;">138-0000-0000 · zsw@email.com</div><div style="height:1px;background:#000;margin-bottom:5px;"></div><div style="text-align:left;font-size:5px;line-height:1.6;color:#333;"><div style="font-weight:700;font-size:6px;margin-bottom:2px;">教育经历</div><div style="margin-bottom:4px;">清华大学 — 计算机科学硕士 | 2021-2024</div><div style="font-weight:700;font-size:6px;margin-bottom:2px;">工作经历</div><div style="margin-bottom:4px;">字节跳动 — 高级产品经理 | 2024-至今</div></div></div>`,
    'executive': `<div class="rt-thumb" style="background:#fff;color:#1a2744;padding:0;font-family:sans-serif;"><div style="background:#1a2744;color:#fff;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;"><div><div style="font-size:10px;font-weight:800;">张思文</div><div style="font-size:5px;opacity:0.8;">高级产品总监</div></div><div style="width:22px;height:22px;background:rgba(255,255,255,.2);border-radius:50%;"></div></div><div style="padding:6px 10px;"><div style="font-size:5px;color:#666;margin-bottom:4px;">北京 · 50K-70K · 10年经验</div><div style="font-size:4px;color:#333;line-height:1.5;"><div style="font-weight:700;color:#1a2744;margin-bottom:1px;">教育背景</div><div style="margin-bottom:3px;">北大光华 MBA | 2018-2020</div><div style="font-weight:700;color:#1a2744;margin-bottom:1px;">工作经历</div><div>阿里巴巴 — 产品总监 | 2020-至今</div></div></div></div>`,
    'modern-tech': `<div class="rt-thumb" style="background:#fff;color:#1e293b;font-family:sans-serif;"><div style="background:linear-gradient(135deg,#2563eb,#7c3aed);color:#fff;padding:8px 10px;text-align:center;"><div style="font-size:10px;font-weight:800;">张思文</div><div style="font-size:5px;opacity:0.9;">全栈开发工程师</div></div><div style="padding:6px 10px;"><div style="display:flex;gap:4px;margin-bottom:4px;flex-wrap:wrap;"><span style="font-size:4px;background:#eff6ff;color:#2563eb;padding:1px 4px;border-radius:2px;">React</span><span style="font-size:4px;background:#eff6ff;color:#2563eb;padding:1px 4px;border-radius:2px;">TypeScript</span><span style="font-size:4px;background:#eff6ff;color:#2563eb;padding:1px 4px;border-radius:2px;">Python</span></div><div style="font-size:4px;color:#475569;line-height:1.5;"><div style="font-weight:700;font-size:5px;color:#2563eb;margin-bottom:1px;">工作经验</div><div>腾讯 · 高级前端 | 2022-至今</div></div></div></div>`,
    'creative-design': `<div class="rt-thumb" style="background:#fff;font-family:sans-serif;"><div style="background:linear-gradient(135deg,#7c3aed,#ec4899);color:#fff;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;"><div><div style="font-size:10px;font-weight:800;">张思文</div><div style="font-size:5px;opacity:0.9;">UI/UX 设计师</div></div><div style="font-size:14px;">🎨</div></div><div style="padding:6px 10px;"><div style="display:flex;gap:3px;margin-bottom:4px;"><div style="width:16px;height:10px;background:#f3f4f6;border-radius:1px;"></div><div style="width:16px;height:10px;background:#f3f4f6;border-radius:1px;"></div></div><div style="font-size:4px;color:#4b5563;line-height:1.5;"><div style="font-weight:700;color:#7c3aed;margin-bottom:1px;">设计技能</div><div>Figma · Sketch · Adobe XD</div></div></div></div>`,
    'elegant': `<div class="rt-thumb" style="background:#fffbeb;color:#78350f;font-family:serif;"><div style="border-bottom:2px solid #b45309;padding:8px 10px;text-align:center;"><div style="font-size:11px;font-weight:800;letter-spacing:2px;">张思文</div><div style="font-size:5px;color:#92400e;margin-top:2px;">管理咨询顾问</div></div><div style="padding:6px 10px;"><div style="font-size:5px;color:#78350f;margin-bottom:3px;">北京 · 40K-60K · 8年经验</div><div style="font-size:4px;color:#78350f;line-height:1.5;"><div style="font-weight:700;color:#b45309;margin-bottom:1px;">教育背景</div><div style="margin-bottom:3px;">清华经管 MBA | 2019-2021</div><div style="font-weight:700;color:#b45309;margin-bottom:1px;">工作经历</div><div>麦肯锡 · 咨询经理 | 2021-至今</div></div></div></div>`,
    'modern-minimal': `<div class="rt-thumb" style="background:#fff;font-family:sans-serif;"><div style="background:linear-gradient(135deg,#7c3aed,#a78bfa);color:#fff;padding:6px 10px;text-align:center;"><div style="font-size:8px;font-weight:800;letter-spacing:2px;">个人简历</div><div style="font-size:4px;opacity:0.8;">PERSONAL RESUME</div></div><div style="padding:5px 10px;"><div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;font-size:4px;color:#4b5563;margin-bottom:4px;"><div>姓名: 张思文</div><div>职位: 产品经理</div><div>电话: 138-0000-0000</div><div>邮箱: zsw@email.com</div></div><div style="font-size:4px;color:#7c3aed;font-weight:700;margin-bottom:2px;">核心技能</div><div style="display:flex;gap:2px;flex-wrap:wrap;"><span style="font-size:3px;background:#f5f3ff;color:#7c3aed;padding:1px 3px;">战略规划</span><span style="font-size:3px;background:#f5f3ff;color:#7c3aed;padding:1px 3px;">数据分析</span></div></div></div>`,
  };
  return map[id] || map['minimal-clean'];
};

const getTemplateHtml = (id: string, accent: string): string => {
  if (id === 'minimal-clean') {
    return `<div class="r r-minimal">
<div class="r-minimal-head">
  <h1>张思文</h1>
  <div class="r-minimal-info">
    <span>产品经理</span><span class="r-dot">·</span><span>北京</span><span class="r-dot">·</span><span>30K-40K</span>
  </div>
  <div class="r-minimal-contact">
    <span>📱 138-0000-0000</span><span>✉️ zsw@email.com</span><span>🔗 github.com/zsw</span>
  </div>
</div>
<div class="r-minimal-body">
  <section>
    <h2>教育经历</h2>
    <div class="r-minimal-entry">
      <div class="r-entry-row"><strong>清华大学</strong><span>2021.09 — 2024.06</span></div>
      <div class="r-entry-sub">计算机科学与技术 · 硕士 · GPA 3.8/4.0</div>
      <p class="r-entry-desc">研究方向为自然语言处理，发表CCF-A论文2篇。获国家奖学金、优秀毕业生称号。</p>
    </div>
    <div class="r-minimal-entry">
      <div class="r-entry-row"><strong>浙江大学</strong><span>2017.09 — 2021.06</span></div>
      <div class="r-entry-sub">软件工程 · 学士 · GPA 3.7/4.0</div>
    </div>
  </section>
  <section>
    <h2>工作经历</h2>
    <div class="r-minimal-entry">
      <div class="r-entry-row"><strong>字节跳动</strong><span>2024.07 — 至今</span></div>
      <div class="r-entry-sub">高级产品经理</div>
      <ul class="r-entry-list"><li>主导抖音电商推荐系统产品迭代，DAU提升23%，GMV增长45%</li><li>设计并落地用户画像标签体系，覆盖8亿用户，精准度提升至92%</li><li>协调算法、工程、运营三线团队，管理6人产品小组，完成15个核心需求</li></ul>
    </div>
    <div class="r-minimal-entry">
      <div class="r-entry-row"><strong>阿里巴巴</strong><span>2022.03 — 2024.06</span></div>
      <div class="r-entry-sub">产品经理（实习转正）</div>
      <ul class="r-entry-list"><li>负责淘宝推荐流产品优化，AB实验驱动点击率提升15%</li><li>搭建数据看板体系，实现核心指标日级监控与异动归因自动化</li></ul>
    </div>
  </section>
  <section>
    <h2>项目经历</h2>
    <div class="r-minimal-entry">
      <div class="r-entry-row"><strong>智能客服机器人</strong><span>2023.03 — 2023.12</span></div>
      <div class="r-entry-sub">项目负责人</div>
      <p class="r-entry-desc">基于LLM构建智能客服系统，支持多轮对话与知识库检索。日处理咨询量50万+，人工转接率降低至8%，年度节省客服成本约200万元。</p>
    </div>
  </section>
  <section>
    <h2>技能 &amp; 其他</h2>
    <div class="r-skill-row"><strong>技术能力</strong> Python, SQL, Tableau, Figma, Axure, Google Analytics</div>
    <div class="r-skill-row"><strong>语言能力</strong> 英语 CET-6（600+），流利商务口语与文档读写</div>
    <div class="r-skill-row"><strong>证书荣誉</strong> PMP认证, NPDP产品经理认证, 2023年度优秀员工</div>
  </section>
</div></div>`;
  }

  if (id === 'executive') {
    return `<div class="r r-exec">
<div class="r-exec-head">
  <div class="r-exec-head-l">
    <h1>张思文</h1>
    <div class="r-exec-title">高级产品总监</div>
    <div class="r-exec-meta">
      <span>北京</span><span class="r-exec-sep">|</span><span>50K-70K</span><span class="r-exec-sep">|</span><span>10年经验</span><span class="r-exec-sep">|</span><span>中共党员</span>
    </div>
    <div class="r-exec-contact">
      <span>138-0000-0000</span><span class="r-exec-sep">|</span><span>zsw@email.com</span>
    </div>
  </div>
  <div class="r-exec-head-r">
    <div class="r-exec-avatar"></div>
  </div>
</div>
<div class="r-exec-body">
  <section>
    <div class="r-exec-banner">教育背景</div>
    <div class="r-exec-entry">
      <div class="r-exec-entry-row"><strong>北京大学光华管理学院</strong><span class="r-exec-date">2018.09 — 2020.07</span></div>
      <div class="r-exec-entry-sub">工商管理硕士（MBA）· GPA 3.7/4.0</div>
      <p class="r-exec-p">研究方向为企业战略与组织管理。获光华奖学金，优秀毕业论文。在校期间担任商学院联合会主席。</p>
    </div>
    <div class="r-exec-entry">
      <div class="r-exec-entry-row"><strong>复旦大学</strong><span class="r-exec-date">2009.09 — 2013.07</span></div>
      <div class="r-exec-entry-sub">计算机科学与技术 · 学士 · GPA 3.5/4.0</div>
      <p class="r-exec-p">主修课程：数据结构、算法设计、操作系统、数据库原理、计算机网络、软件工程。</p>
    </div>
  </section>
  <section>
    <div class="r-exec-banner">工作经历</div>
    <div class="r-exec-entry">
      <div class="r-exec-entry-row"><strong>阿里巴巴集团</strong><span class="r-exec-date">2020.08 — 至今</span></div>
      <div class="r-exec-entry-sub">产品总监 · 电商事业部</div>
      <ul class="r-exec-list"><li>统筹淘宝推荐系统产品战略，管理12人产品团队，制定季度OKR并追踪落地</li><li>主导"千人千面"个性化推荐项目，DAU提升28%，用户平均停留时长增长35%</li><li>推动AI驱动的商品理解体系建设，自动化打标准确率从78%提升至94%</li><li>跨部门协调算法、工程、运营、商业化团队，确保产品迭代周期缩短40%</li></ul>
    </div>
    <div class="r-exec-entry">
      <div class="r-exec-entry-row"><strong>腾讯科技</strong><span class="r-exec-date">2015.07 — 2020.07</span></div>
      <div class="r-exec-entry-sub">高级产品经理 → 产品副总监 · 社交事业群</div>
      <ul class="r-exec-list"><li>负责QQ空间信息流产品规划与迭代，用户活跃度提升18%</li><li>从零搭建内容审核中台产品，日均处理违规内容50万条，误杀率低于0.1%</li></ul>
    </div>
  </section>
  <section>
    <div class="r-exec-banner">核心能力</div>
    <div class="r-exec-skills">
      <span>产品战略规划</span><span>团队管理</span><span>数据分析</span><span>用户研究</span><span>敏捷开发</span><span>A/B实验</span><span>商业化变现</span><span>跨部门协作</span>
    </div>
  </section>
</div></div>`;
  }

  if (id === 'modern-tech') {
    return `<div class="r r-tech">
<div class="r-tech-head">
  <div class="r-tech-head-l">
    <h1>张思文</h1>
    <div class="r-tech-role">全栈开发工程师</div>
    <div class="r-tech-contact">
      <span>北京</span><span>|</span><span>3年经验</span><span>|</span><span>138-0000-0000</span><span>|</span><span>zsw@email.com</span>
    </div>
  </div>
  <div class="r-tech-head-r">
    <div class="r-tech-stack"><span>React</span><span>TypeScript</span><span>Python</span><span>Go</span></div>
  </div>
</div>
<div class="r-tech-body">
  <section>
    <h2>技术能力</h2>
    <div class="r-tech-skill-row"><span class="r-tech-label">前端</span><span>React, Vue 3, TypeScript, Next.js, TailwindCSS, Zustand</span></div>
    <div class="r-tech-skill-row"><span class="r-tech-label">后端</span><span>Python (FastAPI, Django), Go, Node.js, PostgreSQL, Redis, RabbitMQ</span></div>
    <div class="r-tech-skill-row"><span class="r-tech-label">DevOps</span><span>Docker, Kubernetes, AWS (EC2, S3, Lambda), GitHub Actions, Terraform</span></div>
  </section>
  <section>
    <h2>工作经历</h2>
    <div class="r-tech-entry">
      <div class="r-tech-entry-head"><strong>字节跳动</strong> — 高级前端工程师<span>2023.06 — 至今</span></div>
      <ul class="r-tech-list"><li>主导飞书文档前端架构升级，Micro-Frontend方案拆解巨石应用，构建时间减少70%</li><li>设计并实现协同编辑冲突解决算法（CRDT），支持100人同时在线编辑，延迟 < 50ms</li><li>推动组件库建设，封装50+业务组件，跨团队复用率达80%</li></ul>
    </div>
    <div class="r-tech-entry">
      <div class="r-tech-entry-head"><strong>美团</strong> — 前端开发工程师<span>2021.07 — 2023.05</span></div>
      <ul class="r-tech-list"><li>负责商家端后台管理系统前端开发，使用React + TypeScript重构旧版jQuery项目</li><li>优化首屏加载性能，LCP从4.2s降至1.1s，Lighthouse评分从45提升至92</li></ul>
    </div>
  </section>
  <section>
    <h2>教育背景</h2>
    <div class="r-tech-entry">
      <div class="r-tech-entry-head"><strong>华中科技大学</strong> — 软件工程 · 硕士<span>2019.09 — 2021.06</span></div>
    </div>
  </section>
  <section>
    <h2>开源项目</h2>
    <div class="r-tech-entry">
      <div class="r-tech-entry-head"><strong>react-virtuoso</strong> — Core Contributor<span>2022.03 — 至今</span></div>
      <p class="r-tech-p">为大型列表虚拟滚动库贡献了Window Scroller支持与动态高度测量优化，GitHub 13k+ Stars。</p>
    </div>
  </section>
</div></div>`;
  }

  if (id === 'creative-design') {
    return `<div class="r r-creative">
<div class="r-creative-banner">
  <div class="r-creative-banner-l">
    <h1>张思文</h1>
    <div class="r-creative-title">UI/UX 设计师</div>
    <div class="r-creative-motto">"设计是解决问题的艺术"</div>
  </div>
  <div class="r-creative-banner-r">
    <div class="r-creative-avatar">🎨</div>
  </div>
</div>
<div class="r-creative-body">
  <div class="r-creative-grid">
    <div class="r-creative-main">
      <section>
        <div class="r-creative-block">工作经历</div>
        <div class="r-creative-work">
          <div class="r-creative-work-head"><strong>网易</strong><span>2022.03 — 至今</span></div>
          <div class="r-creative-work-role">高级UI设计师</div>
          <ul><li>主导网易云音乐App 9.0改版设计，DAU提升18%，App Store评分从4.2升至4.7</li><li>建立设计规范系统（Design System），统一80+页面视觉语言</li><li>与产品、开发协作完成会员中心全链路改版，付费转化率提升32%</li></ul>
        </div>
        <div class="r-creative-work">
          <div class="r-creative-work-head"><strong>小红书</strong><span>2020.07 — 2022.02</span></div>
          <div class="r-creative-work-role">UI设计师</div>
          <ul><li>负责社区内容流设计，优化图文笔记浏览体验，用户浏览深度提升25%</li><li>主导设计小红书品牌营销活动中台，服务1000+品牌客户</li></ul>
        </div>
      </section>
      <section>
        <div class="r-creative-block">教育背景</div>
        <div class="r-creative-edu">
          <div><strong>中国美术学院</strong><span>2016.09 — 2020.06</span></div>
          <div class="r-creative-edu-sub">视觉传达设计 · 学士 · GPA 3.8/4.0</div>
        </div>
      </section>
    </div>
    <div class="r-creative-side">
      <section>
        <div class="r-creative-block">设计技能</div>
        <div class="r-creative-skillbar"><span>Figma</span><div class="r-creative-bar"><i style="width:96%"></i></div></div>
        <div class="r-creative-skillbar"><span>Sketch</span><div class="r-creative-bar"><i style="width:88%"></i></div></div>
        <div class="r-creative-skillbar"><span>Adobe XD</span><div class="r-creative-bar"><i style="width:82%"></i></div></div>
        <div class="r-creative-skillbar"><span>After Effects</span><div class="r-creative-bar"><i style="width:75%"></i></div></div>
      </section>
      <section>
        <div class="r-creative-block">联系方式</div>
        <div class="r-creative-contact-list">
          <div>📱 138-0000-0000</div>
          <div>✉️ zsw@email.com</div>
          <div>🔗 dribbble.com/zsw</div>
          <div>📍 北京</div>
        </div>
      </section>
    </div>
  </div>
</div></div>`;
  }

  if (id === 'elegant') {
    return `<div class="r r-elegant">
<div class="r-elegant-head">
  <h1>张思文</h1>
  <div class="r-elegant-subtitle">管理咨询顾问</div>
  <div class="r-elegant-contact">
    <span>北京</span><span class="r-elegant-sep">|</span><span>8年经验</span><span class="r-elegant-sep">|</span><span>40K-60K</span><span class="r-elegant-sep">|</span><span>138-0000-0000</span><span class="r-elegant-sep">|</span><span>zsw@email.com</span>
  </div>
</div>
<div class="r-elegant-body">
  <section>
    <h2>教育背景</h2>
    <div class="r-elegant-entry">
      <div class="r-elegant-entry-row"><strong>清华大学经济管理学院</strong><span>2019.09 — 2021.07</span></div>
      <div class="r-elegant-entry-sub">工商管理硕士（MBA）· 优秀毕业生</div>
    </div>
    <div class="r-elegant-entry">
      <div class="r-elegant-entry-row"><strong>中国人民大学</strong><span>2010.09 — 2014.07</span></div>
      <div class="r-elegant-entry-sub">经济学 · 学士 · 北京市优秀毕业生</div>
    </div>
  </section>
  <section>
    <h2>工作经历</h2>
    <div class="r-elegant-entry">
      <div class="r-elegant-entry-row"><strong>麦肯锡咨询</strong><span>2021.07 — 至今</span></div>
      <div class="r-elegant-entry-sub">咨询经理 · 金融与科技组</div>
      <ul><li>主导12+战略咨询项目，覆盖金融科技、消费零售、智能制造三大赛道</li><li>为某头部城商行设计数字化转型路线图，帮助客户实现年化营收增长23%</li><li>带领5人顾问团队完成某新能源车企供应链优化项目，降低成本1.2亿元/年</li></ul>
    </div>
    <div class="r-elegant-entry">
      <div class="r-elegant-entry-row"><strong>德勤咨询</strong><span>2014.09 — 2019.07</span></div>
      <div class="r-elegant-entry-sub">高级顾问 · 战略与运营组</div>
      <ul><li>参与15+大型企业数字化转型咨询项目，服务客户包括多家世界500强</li><li>独立完成3个行业白皮书撰写，获公司年度最佳研究报告奖</li></ul>
    </div>
  </section>
  <section>
    <h2>核心能力</h2>
    <div class="r-elegant-skills">
      <span>战略规划</span><span>商业分析</span><span>项目管理</span><span>数据分析</span><span>团队领导</span><span>客户关系</span><span>PPT/Excel</span><span>SQL/Python</span>
    </div>
  </section>
</div></div>`;
  }

  if (id === 'modern-minimal') {
    return `<div class="r r-modern">
<div class="r-modern-banner">
  <div class="r-modern-banner-l">
    <div class="r-modern-label">PERSONAL RESUME</div>
    <h1>个人简历</h1>
    <div class="r-modern-slogan">专业 · 高效 · 创新</div>
  </div>
  <div class="r-modern-banner-r">
    <div class="r-modern-hex">💼</div>
  </div>
</div>
<div class="r-modern-body">
  <section>
    <div class="r-modern-block"><span></span>基本信息</div>
    <div class="r-modern-info-grid">
      <div><label>姓名</label><span>张思文</span></div>
      <div><label>职位</label><span>产品经理</span></div>
      <div><label>电话</label><span>138-0000-0000</span></div>
      <div><label>邮箱</label><span>zsw@email.com</span></div>
      <div><label>地点</label><span>北京</span></div>
      <div><label>经验</label><span>3年</span></div>
    </div>
  </section>
  <section>
    <div class="r-modern-block"><span></span>教育背景</div>
    <div class="r-modern-edu">
      <div><strong>上海交通大学</strong><span>2020.09 — 2023.06</span></div>
      <div class="r-modern-sub">电子信息工程 · 硕士</div>
    </div>
  </section>
  <section>
    <div class="r-modern-block"><span></span>工作经历</div>
    <div class="r-modern-work">
      <div class="r-modern-work-head"><strong>拼多多</strong><span>2023.07 — 至今</span></div>
      <div class="r-modern-work-role">产品经理 · 推荐策略组</div>
      <ul><li>主导拼多多首页推荐Feed产品迭代，用户点击率提升18%，GMV增长32%</li><li>设计品类偏好标签体系，推荐精准度从81%提升至91%</li></ul>
    </div>
  </section>
  <section>
    <div class="r-modern-block"><span></span>核心技能</div>
    <div class="r-modern-tags">
      <span>需求分析</span><span>数据驱动</span><span>A/B实验</span><span>SQL</span><span>Axure</span><span>项目管理</span>
    </div>
  </section>
</div></div>`;
  }

  return getTemplateHtml('minimal-clean', accent);
};

// ═══ Data ═══

const templates: Template[] = [
  { id: 'minimal-clean', name: '极简瑞士', description: '黑白配色，强排版节奏，信息层级分明，适合各类岗位', category: 'minimal', tags: ['通用', '极简', '现代'], accentColor: '#111111' },
  { id: 'executive', name: '深蓝专业', description: '深蓝色调，稳重权威，适合中高层管理与商务岗位', category: 'professional', tags: ['管理', '商务', '正式'], accentColor: '#1a2744' },
  { id: 'modern-tech', name: '科技蓝调', description: 'Tech风格，技能标签突出，适合技术研发与互联网岗位', category: 'professional', tags: ['技术', 'IT', '互联网'], accentColor: '#2563eb' },
  { id: 'creative-design', name: '创意工坊', description: '渐变配色，侧栏布局，适合设计创意与艺术类岗位', category: 'creative', tags: ['设计', '创意', '个性'], accentColor: '#7c3aed' },
  { id: 'elegant', name: '温暖经典', description: '温暖金棕色调，衬线风格，适合金融咨询与专业服务', category: 'professional', tags: ['金融', '咨询', '优雅'], accentColor: '#b45309' },
  { id: 'modern-minimal', name: '紫韵现代', description: '渐变紫金banner，网格信息布局，适合各专业岗位', category: 'minimal', tags: ['现代', '简约', '专业'], accentColor: '#7c3aed' },
].map(t => ({ ...t, htmlContent: getTemplateHtml(t.id, t.accentColor) }));

const activeCategory = ref('all');
const activeId = ref(templates[0].id);

const filteredTemplates = computed(() => {
  if (activeCategory.value === 'all') return templates;
  return templates.filter(t => t.category === activeCategory.value);
});

const activeTemplate = computed(() => templates.find(t => t.id === activeId.value));

function useActive() {
  emit('selectTemplate', activeId.value);
}
</script>

<style scoped>
/* ═══ Shell ═══ */
.tl-shell {
  display: flex;
  height: 100%;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: tl-in 0.4s ease;
}
@keyframes tl-in {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

/* ═══ Sidebar ═══ */
.tl-sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: var(--border-subtle);
  background: var(--bg-primary);
}

.tl-sidebar-header {
  padding: 24px 20px 16px;
  flex-shrink: 0;
}

.tl-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--white);
  margin: 0 0 16px 0;
  letter-spacing: -0.01em;
}

.tl-filter {
  display: flex;
  gap: 6px;
}

.tl-filter-btn {
  padding: 6px 14px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--slate-400);
  cursor: pointer;
  transition: all 0.15s ease;
}

.tl-filter-btn:hover { color: var(--white); background: var(--bg-tertiary); }
.tl-filter-btn.on {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  border-color: transparent;
  font-weight: 600;
}

/* ═══ Template List ═══ */
.tl-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 12px;
}

.tl-card {
  display: flex;
  gap: 14px;
  width: 100%;
  padding: 12px;
  margin-bottom: 4px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  color: inherit;
}

.tl-card:hover {
  background: var(--bg-secondary);
  border-color: rgba(255,255,255,0.06);
}

.tl-card.picked {
  background: var(--bg-secondary);
  border-color: rgba(16, 185, 129, 0.35);
  box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.15);
}

.tl-card-visual {
  width: 72px;
  flex-shrink: 0;
}

.tl-card-thumb {
  width: 72px;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  background: #fff;
}

.tl-card-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.tl-card-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 4px;
}

.tl-card-desc {
  font-size: 11px;
  color: var(--slate-400);
  line-height: 1.5;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tl-card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tl-tag {
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  font-size: 10px;
  color: var(--slate-500);
}

.tl-card.picked .tl-tag {
  color: var(--emerald-400);
  background: rgba(16, 185, 129, 0.1);
}

/* ═══ Preview Panel ═══ */
.tl-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-elevated);
  min-width: 0;
}

.tl-preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: var(--border-subtle);
  flex-shrink: 0;
}

.tl-preview-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--white);
}

.tl-preview-hint {
  font-size: 11px;
  color: var(--slate-500);
}

.tl-paper-wrap {
  flex: 1;
  overflow: auto;
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.tl-paper {
  width: 794px;
  min-height: 1123px;
  background: #fff;
  box-shadow: 0 4px 32px rgba(0,0,0,0.3), 0 0 0 1px rgba(0,0,0,0.08);
  transform-origin: top center;
  transform: scale(0.72);
  margin-bottom: calc(-1123px * 0.28);
  flex-shrink: 0;
}

.tl-preview-actions {
  padding: 16px 24px;
  border-top: var(--border-subtle);
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.tl-use-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 40px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-xl);
  font-size: 15px;
  font-weight: 600;
  color: var(--bg-primary);
  cursor: pointer;
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.25);
  transition: all 0.2s ease;
}

.tl-use-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 40px rgba(16, 185, 129, 0.4);
}

/* ═══ Thumbnail mini previews ═══ */
.tl-card-thumb :deep(.rt-thumb) {
  width: 100%;
  height: 100%;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  line-height: 1.4;
  overflow: hidden;
}

/* ═══ Resume Template Styles ═══ */
.tl-resume :deep(.r) {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  color: #1a1a1a;
  line-height: 1.6;
}

/* ── Minimal Clean ── */
.tl-resume :deep(.r-minimal) { padding: 56px 64px; }
.tl-resume :deep(.r-minimal-head) { text-align: center; margin-bottom: 40px; }
.tl-resume :deep(.r-minimal-head h1) { font-size: 38px; font-weight: 800; letter-spacing: 4px; margin: 0 0 12px; color: #000; }
.tl-resume :deep(.r-minimal-info) { font-size: 15px; color: #555; margin-bottom: 8px; }
.tl-resume :deep(.r-minimal-info .r-dot) { margin: 0 8px; color: #ccc; }
.tl-resume :deep(.r-minimal-contact) { font-size: 13px; color: #777; display: flex; justify-content: center; gap: 20px; }
.tl-resume :deep(.r-minimal-body section) { margin-bottom: 28px; }
.tl-resume :deep(.r-minimal-body h2) { font-size: 15px; font-weight: 700; letter-spacing: 2px; margin: 0 0 8px; color: #000; text-transform: uppercase; }
.tl-resume :deep(.r-minimal-body h2::after) { content: ''; display: block; width: 100%; height: 1px; background: #000; margin-top: 6px; }
.tl-resume :deep(.r-minimal-entry) { margin-bottom: 16px; }
.tl-resume :deep(.r-entry-row) { display: flex; justify-content: space-between; align-items: baseline; font-size: 14px; margin-bottom: 2px; }
.tl-resume :deep(.r-entry-row strong) { font-size: 15px; color: #000; }
.tl-resume :deep(.r-entry-row span) { font-size: 13px; color: #888; }
.tl-resume :deep(.r-entry-sub) { font-size: 13px; color: #555; margin-bottom: 4px; }
.tl-resume :deep(.r-entry-desc) { font-size: 13px; color: #444; margin: 4px 0; line-height: 1.7; }
.tl-resume :deep(.r-entry-list) { margin: 4px 0; padding-left: 18px; font-size: 13px; color: #444; line-height: 1.8; }
.tl-resume :deep(.r-entry-list li) { margin-bottom: 2px; }
.tl-resume :deep(.r-skill-row) { font-size: 13px; color: #444; margin-bottom: 4px; line-height: 1.8; }
.tl-resume :deep(.r-skill-row strong) { color: #000; margin-right: 4px; }

/* ── Executive ── */
.tl-resume :deep(.r-exec) { padding: 0; }
.tl-resume :deep(.r-exec-head) { padding: 40px 56px 28px; background: #f8fafc; border-bottom: 3px solid #1a2744; display: flex; justify-content: space-between; }
.tl-resume :deep(.r-exec-head-l h1) { font-size: 36px; font-weight: 800; color: #1a2744; margin: 0 0 6px; letter-spacing: 2px; }
.tl-resume :deep(.r-exec-title) { font-size: 17px; color: #1a2744; font-weight: 600; margin-bottom: 10px; }
.tl-resume :deep(.r-exec-meta) { font-size: 13px; color: #4b5563; margin-bottom: 4px; }
.tl-resume :deep(.r-exec-contact) { font-size: 13px; color: #4b5563; }
.tl-resume :deep(.r-exec-sep) { margin: 0 8px; color: #cbd5e1; }
.tl-resume :deep(.r-exec-head-r) { }
.tl-resume :deep(.r-exec-avatar) { width: 90px; height: 90px; border-radius: 50%; background: linear-gradient(135deg, #1a2744, #2d4a7a); }
.tl-resume :deep(.r-exec-body) { padding: 28px 56px 48px; }
.tl-resume :deep(.r-exec-body section) { margin-bottom: 24px; }
.tl-resume :deep(.r-exec-banner) { background: #1a2744; color: #fff; padding: 8px 18px; font-size: 14px; font-weight: 700; letter-spacing: 2px; margin-bottom: 14px; display: inline-block; }
.tl-resume :deep(.r-exec-entry) { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #f1f5f9; }
.tl-resume :deep(.r-exec-entry:last-child) { border-bottom: none; }
.tl-resume :deep(.r-exec-entry-row) { display: flex; justify-content: space-between; font-size: 15px; margin-bottom: 4px; }
.tl-resume :deep(.r-exec-entry-row strong) { color: #1a2744; }
.tl-resume :deep(.r-exec-date) { font-size: 13px; color: #3b82f6; font-weight: 500; }
.tl-resume :deep(.r-exec-entry-sub) { font-size: 13px; color: #6b7280; margin-bottom: 6px; }
.tl-resume :deep(.r-exec-p) { font-size: 13px; color: #4b5563; margin: 4px 0; line-height: 1.7; }
.tl-resume :deep(.r-exec-list) { margin: 4px 0; padding-left: 18px; font-size: 13px; color: #4b5563; line-height: 1.8; }
.tl-resume :deep(.r-exec-list li) { margin-bottom: 2px; }
.tl-resume :deep(.r-exec-skills) { display: flex; flex-wrap: wrap; gap: 8px; }
.tl-resume :deep(.r-exec-skills span) { padding: 6px 16px; background: #f1f5f9; color: #1a2744; font-size: 13px; font-weight: 500; border-radius: 4px; }

/* ── Modern Tech ── */
.tl-resume :deep(.r-tech) { padding: 0; }
.tl-resume :deep(.r-tech-head) { padding: 36px 56px; background: linear-gradient(135deg, #2563eb, #7c3aed); color: #fff; display: flex; justify-content: space-between; align-items: center; }
.tl-resume :deep(.r-tech-head-l h1) { font-size: 34px; font-weight: 800; margin: 0 0 4px; letter-spacing: 2px; }
.tl-resume :deep(.r-tech-role) { font-size: 16px; opacity: 0.9; margin-bottom: 8px; font-weight: 500; }
.tl-resume :deep(.r-tech-contact) { font-size: 13px; opacity: 0.85; }
.tl-resume :deep(.r-tech-contact span) { margin-right: 4px; }
.tl-resume :deep(.r-tech-head-r) { }
.tl-resume :deep(.r-tech-stack) { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.tl-resume :deep(.r-tech-stack span) { padding: 6px 14px; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 13px; font-weight: 500; }
.tl-resume :deep(.r-tech-body) { padding: 32px 56px 48px; }
.tl-resume :deep(.r-tech-body section) { margin-bottom: 24px; }
.tl-resume :deep(.r-tech-body h2) { font-size: 16px; font-weight: 700; color: #2563eb; margin: 0 0 12px; padding-bottom: 6px; border-bottom: 2px solid #2563eb; letter-spacing: 1px; }
.tl-resume :deep(.r-tech-skill-row) { font-size: 13px; color: #334155; margin-bottom: 6px; line-height: 1.7; }
.tl-resume :deep(.r-tech-label) { font-weight: 700; color: #2563eb; margin-right: 8px; min-width: 56px; display: inline-block; }
.tl-resume :deep(.r-tech-entry) { margin-bottom: 14px; }
.tl-resume :deep(.r-tech-entry-head) { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 4px; }
.tl-resume :deep(.r-tech-entry-head strong) { color: #1e293b; }
.tl-resume :deep(.r-tech-entry-head span) { font-size: 13px; color: #64748b; }
.tl-resume :deep(.r-tech-list) { margin: 4px 0; padding-left: 18px; font-size: 13px; color: #475569; line-height: 1.8; }
.tl-resume :deep(.r-tech-p) { font-size: 13px; color: #475569; margin: 4px 0; line-height: 1.7; }

/* ── Creative ── */
.tl-resume :deep(.r-creative) { padding: 0; }
.tl-resume :deep(.r-creative-banner) { padding: 44px 56px; background: linear-gradient(135deg, #7c3aed, #ec4899); color: #fff; display: flex; justify-content: space-between; align-items: center; }
.tl-resume :deep(.r-creative-banner-l h1) { font-size: 40px; font-weight: 800; margin: 0 0 6px; letter-spacing: 3px; }
.tl-resume :deep(.r-creative-title) { font-size: 18px; opacity: 0.95; margin-bottom: 8px; font-weight: 500; }
.tl-resume :deep(.r-creative-motto) { font-size: 14px; opacity: 0.8; font-style: italic; }
.tl-resume :deep(.r-creative-avatar) { width: 80px; height: 80px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px; }
.tl-resume :deep(.r-creative-body) { padding: 28px 0 40px; }
.tl-resume :deep(.r-creative-grid) { display: flex; gap: 32px; }
.tl-resume :deep(.r-creative-main) { flex: 1; padding-left: 56px; }
.tl-resume :deep(.r-creative-side) { width: 220px; background: #faf5ff; padding: 24px 20px; }
.tl-resume :deep(.r-creative-block) { font-size: 15px; font-weight: 700; color: #7c3aed; margin-bottom: 12px; letter-spacing: 2px; padding-bottom: 6px; border-bottom: 2px solid #7c3aed; }
.tl-resume :deep(.r-creative-work) { margin-bottom: 18px; }
.tl-resume :deep(.r-creative-work-head) { display: flex; justify-content: space-between; font-size: 15px; margin-bottom: 2px; }
.tl-resume :deep(.r-creative-work-head strong) { color: #1e293b; }
.tl-resume :deep(.r-creative-work-head span) { font-size: 13px; color: #7c3aed; }
.tl-resume :deep(.r-creative-work-role) { font-size: 13px; color: #6b7280; margin-bottom: 6px; }
.tl-resume :deep(.r-creative-work ul) { margin: 4px 0; padding-left: 18px; font-size: 13px; color: #4b5563; line-height: 1.8; }
.tl-resume :deep(.r-creative-edu) { font-size: 14px; }
.tl-resume :deep(.r-creative-edu div:first-child) { display: flex; justify-content: space-between; margin-bottom: 2px; }
.tl-resume :deep(.r-creative-edu div:first-child span) { font-size: 13px; color: #7c3aed; }
.tl-resume :deep(.r-creative-edu-sub) { font-size: 13px; color: #6b7280; }
.tl-resume :deep(.r-creative-skillbar) { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.tl-resume :deep(.r-creative-skillbar span) { font-size: 12px; color: #4b5563; width: 80px; }
.tl-resume :deep(.r-creative-bar) { flex: 1; height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden; }
.tl-resume :deep(.r-creative-bar i) { display: block; height: 100%; background: linear-gradient(90deg, #7c3aed, #ec4899); border-radius: 3px; }
.tl-resume :deep(.r-creative-contact-list) { font-size: 13px; color: #4b5563; line-height: 2; }

/* ── Elegant ── */
.tl-resume :deep(.r-elegant) { padding: 0; }
.tl-resume :deep(.r-elegant-head) { padding: 48px 64px 32px; text-align: center; border-bottom: 3px double #b45309; margin: 0 56px; }
.tl-resume :deep(.r-elegant-head h1) { font-size: 36px; font-weight: 800; color: #78350f; margin: 0 0 8px; letter-spacing: 6px; font-family: 'Noto Serif SC', 'STSong', serif; }
.tl-resume :deep(.r-elegant-subtitle) { font-size: 16px; color: #92400e; margin-bottom: 10px; font-weight: 500; }
.tl-resume :deep(.r-elegant-contact) { font-size: 13px; color: #78716c; }
.tl-resume :deep(.r-elegant-sep) { margin: 0 10px; color: #d6d3d1; }
.tl-resume :deep(.r-elegant-body) { padding: 28px 64px 48px; }
.tl-resume :deep(.r-elegant-body section) { margin-bottom: 28px; }
.tl-resume :deep(.r-elegant-body h2) { font-size: 17px; font-weight: 700; color: #78350f; margin: 0 0 12px; letter-spacing: 2px; border-bottom: 1px solid #e7d7c4; padding-bottom: 8px; }
.tl-resume :deep(.r-elegant-entry) { margin-bottom: 18px; }
.tl-resume :deep(.r-elegant-entry-row) { display: flex; justify-content: space-between; font-size: 15px; margin-bottom: 4px; }
.tl-resume :deep(.r-elegant-entry-row strong) { color: #78350f; }
.tl-resume :deep(.r-elegant-entry-row span) { font-size: 13px; color: #a8a29e; }
.tl-resume :deep(.r-elegant-entry-sub) { font-size: 13px; color: #78716c; margin-bottom: 6px; }
.tl-resume :deep(.r-elegant-body ul) { margin: 4px 0; padding-left: 18px; font-size: 13px; color: #57534e; line-height: 1.8; }
.tl-resume :deep(.r-elegant-body ul li) { margin-bottom: 2px; }
.tl-resume :deep(.r-elegant-skills) { display: flex; flex-wrap: wrap; gap: 10px; }
.tl-resume :deep(.r-elegant-skills span) { padding: 8px 20px; background: #fffbeb; color: #78350f; border: 1px solid #e7d7c4; font-size: 13px; border-radius: 2px; }

/* ── Modern Minimal ── */
.tl-resume :deep(.r-modern) { padding: 0; }
.tl-resume :deep(.r-modern-banner) { padding: 40px 56px; background: linear-gradient(135deg, #7c3aed, #a78bfa); color: #fff; display: flex; justify-content: space-between; align-items: center; }
.tl-resume :deep(.r-modern-label) { font-size: 10px; letter-spacing: 4px; opacity: 0.8; margin-bottom: 8px; text-transform: uppercase; }
.tl-resume :deep(.r-modern-banner-l h1) { font-size: 42px; font-weight: 800; margin: 0 0 6px; letter-spacing: 8px; }
.tl-resume :deep(.r-modern-slogan) { font-size: 14px; opacity: 0.9; }
.tl-resume :deep(.r-modern-hex) { width: 90px; height: 90px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; font-size: 40px; clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); }
.tl-resume :deep(.r-modern-body) { padding: 32px 56px 48px; }
.tl-resume :deep(.r-modern-body section) { margin-bottom: 24px; }
.tl-resume :deep(.r-modern-block) { display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 700; color: #7c3aed; margin-bottom: 14px; letter-spacing: 2px; }
.tl-resume :deep(.r-modern-block span) { width: 4px; height: 20px; background: linear-gradient(180deg, #7c3aed, #a78bfa); border-radius: 2px; display: inline-block; }
.tl-resume :deep(.r-modern-info-grid) { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px 32px; }
.tl-resume :deep(.r-modern-info-grid div) { font-size: 14px; }
.tl-resume :deep(.r-modern-info-grid label) { color: #9ca3af; font-size: 12px; display: block; margin-bottom: 2px; }
.tl-resume :deep(.r-modern-info-grid span) { color: #1f2937; font-weight: 600; }
.tl-resume :deep(.r-modern-edu) { font-size: 14px; }
.tl-resume :deep(.r-modern-edu div:first-child) { display: flex; justify-content: space-between; margin-bottom: 4px; }
.tl-resume :deep(.r-modern-edu div:first-child span) { font-size: 13px; color: #7c3aed; }
.tl-resume :deep(.r-modern-sub) { font-size: 13px; color: #6b7280; }
.tl-resume :deep(.r-modern-work) { margin-bottom: 8px; }
.tl-resume :deep(.r-modern-work-head) { display: flex; justify-content: space-between; font-size: 15px; margin-bottom: 2px; }
.tl-resume :deep(.r-modern-work-head strong) { color: #1f2937; }
.tl-resume :deep(.r-modern-work-head span) { font-size: 13px; color: #7c3aed; }
.tl-resume :deep(.r-modern-work-role) { font-size: 13px; color: #6b7280; margin-bottom: 6px; }
.tl-resume :deep(.r-modern-body ul) { margin: 4px 0; padding-left: 18px; font-size: 13px; color: #4b5563; line-height: 1.8; }
.tl-resume :deep(.r-modern-tags) { display: flex; flex-wrap: wrap; gap: 8px; }
.tl-resume :deep(.r-modern-tags span) { padding: 8px 18px; background: linear-gradient(135deg, #f5f3ff, #ede9fe); color: #7c3aed; font-size: 13px; font-weight: 500; border-left: 3px solid #7c3aed; }

/* ═══ Responsive ═══ */
@media (max-width: 1100px) {
  .tl-shell { flex-direction: column; height: auto; max-height: none; }
  .tl-sidebar { width: 100%; border-right: none; border-bottom: var(--border-subtle); max-height: 280px; }
  .tl-paper-wrap { padding: 16px; }
  .tl-paper { transform: scale(0.55); margin-bottom: calc(-1123px * 0.45); }
}
@media (max-width: 768px) {
  .tl-sidebar-header { padding: 16px 12px 12px; }
  .tl-title { font-size: 18px; margin-bottom: 10px; }
  .tl-list { padding: 0 8px 8px; }
  .tl-card { padding: 10px; }
  .tl-card-visual { width: 52px; }
  .tl-card-thumb { width: 52px; height: 72px; }
  .tl-card-name { font-size: 13px; }
  .tl-card-desc { font-size: 10px; }
  .tl-paper { transform: scale(0.42); margin-bottom: calc(-1123px * 0.58); }
}
</style>
