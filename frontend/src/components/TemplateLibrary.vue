<template>
  <div class="template-library">
    <div class="library-header">
      <div class="header-content">
        <h2 class="library-title">精选模板库</h2>
        <p class="library-subtitle">
          精心挑选的专业简历模板，简约大气，盲选也不会出错
        </p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-number">{{ templates.length }}</span>
          <span class="stat-text">精选模板</span>
        </div>
      </div>
    </div>

    <div class="template-filters">
      <button 
        v-for="cat in categories" 
        :key="cat.id"
        class="filter-btn"
        :class="{ active: activeCategory === cat.id }"
        @click="activeCategory = cat.id"
      >
        {{ cat.label }}
      </button>
    </div>

    <div class="templates-grid">
      <div 
        v-for="template in filteredTemplates" 
        :key="template.id"
        class="template-card"
        :class="{ featured: template.featured }"
      >
        <div class="card-preview">
          <div class="preview-paper" :style="{ background: template.previewBg }">
            <div 
              class="template-mini-preview"
              :style="{ '--accent-color': template.accentColor }"
              v-html="getMiniPreviewHtml(template.id, template.accentColor)"
            ></div>
          </div>
          <div class="preview-overlay">
            <button class="preview-btn" @click="previewTemplate(template)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <span>预览</span>
            </button>
          </div>
        </div>

        <div class="card-info">
          <div class="card-header">
            <h3 class="card-title">{{ template.name }}</h3>
            <span v-if="template.featured" class="featured-badge">推荐</span>
          </div>
          <p class="card-desc">{{ template.description }}</p>
          <div class="card-tags">
            <span 
              v-for="tag in template.tags" 
              :key="tag" 
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="card-actions">
          <button class="action-btn primary full" @click="useTemplate(template)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            <span>使用模板</span>
          </button>
        </div>
      </div>
    </div>

    <div class="tips-section">
      <div class="tips-card">
        <div class="tips-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <div class="tips-content">
          <h4 class="tips-title">模板使用提示</h4>
          <ul class="tips-list">
            <li>选择与目标岗位匹配的模板风格</li>
            <li>下载PDF后可用PDF编辑器填写内容</li>
            <li>保持内容简洁，突出重点成就</li>
            <li>导出前检查格式和排版细节</li>
          </ul>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showPreview" class="preview-modal" @click.self="showPreview = false">
        <div class="modal-content large">
          <div class="modal-header">
            <h3>{{ selectedTemplate?.name }}</h3>
            <button class="close-btn" @click="showPreview = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div 
              ref="templatePreviewRef" 
              class="template-preview-full"
              :style="{ '--accent-color': selectedTemplate?.accentColor }"
              v-html="selectedTemplate?.htmlContent"
            ></div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn secondary" @click="showPreview = false">关闭</button>
            <button class="modal-btn primary" @click="useSelectedTemplate">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;margin-right:6px;">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              使用此模板
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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
  featured: boolean;
  previewBg: string;
  accentColor: string;
  htmlContent: string;
}

const categories = [
  { id: 'all', label: '全部' },
  { id: 'professional', label: '专业商务' },
  { id: 'creative', label: '创意设计' },
  { id: 'minimal', label: '简约清新' },
];

const getTemplateHtml = (id: string, accentColor: string): string => {
  const templates: Record<string, string> = {
    'executive': `
      <div class="resume-template executive-pro">
        <div class="resume-header-pro">
          <div class="header-left">
            <h1 class="name-title">姓名</h1>
            <div class="info-lines">
              <p class="info-line job-intention">
                <span class="info-label">求职意向：</span>
                <span>[目标岗位]</span>
                <span class="separator">|</span>
                <span>[期望城市]</span>
                <span class="separator">|</span>
                <span>[期望薪资]</span>
                <span class="separator">|</span>
                <span>[可面议]</span>
              </p>
              <p class="info-line basic-info">
                <span class="info-label">基本信息：</span>
                <span>[年龄] 岁</span>
                <span class="separator">|</span>
                <span>[性别]</span>
                <span class="separator">|</span>
                <span>[工作年限] 经验</span>
                <span class="separator">|</span>
                <span>[所在公司]</span>
              </p>
              <p class="info-line contact-info">
                <span class="info-label">联系方式：</span>
                <span>[手机号码]</span>
                <span class="separator">|</span>
                <span>[电子邮箱]</span>
              </p>
            </div>
          </div>
          <div class="header-right">
            <div class="avatar-pro">
              <svg viewBox="0 0 100 100" class="avatar-svg">
                <circle cx="50" cy="35" r="25" fill="#f5d0c5"/>
                <ellipse cx="50" cy="90" rx="35" ry="25" fill="#2c3e50"/>
                <rect x="35" y="55" width="30" height="20" fill="#ffffff" rx="2"/>
                <path d="M 40 75 L 50 85 L 60 75" fill="#c0392b"/>
                <circle cx="42" cy="32" r="3" fill="#2c3e50"/>
                <circle cx="58" cy="32" r="3" fill="#2c3e50"/>
                <rect x="38" y="28" width="8" height="6" fill="none" stroke="#2c3e50" stroke-width="1.5" rx="1"/>
                <rect x="54" y="28" width="8" height="6" fill="none" stroke="#2c3e50" stroke-width="1.5" rx="1"/>
                <path d="M 46 28 L 46 34 M 54 28 L 54 34" stroke="#2c3e50" stroke-width="1"/>
                <path d="M 35 20 Q 50 10 65 20" fill="#4a3728"/>
                <path d="M 35 20 Q 50 25 65 20" fill="#4a3728"/>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="resume-body-pro">
          <section class="section-pro">
            <div class="section-banner" style="background: ${accentColor};">
              <h3>教育背景</h3>
            </div>
            <div class="section-content">
              <div class="entry-item">
                <div class="entry-header">
                  <span class="entry-date">[起始日期 A] ～ [结束日期 B]</span>
                  <span class="entry-title">[学校名称]</span>
                  <span class="entry-subtitle">[专业及学位]</span>
                </div>
                <div class="entry-details">
                  <p class="detail-line">[学业表现，如：GPA X.X/X（专业前X%）]</p>
                  <p class="detail-courses">[主修课程：课程1、课程2、课程3、课程4、课程5、课程6、课程7、课程8...]</p>
                </div>
              </div>
              <div class="entry-item">
                <div class="entry-header">
                  <span class="entry-date">[起始日期 C] ～ [结束日期 D]</span>
                  <span class="entry-title">[学校名称]</span>
                  <span class="entry-subtitle">[专业及学位]</span>
                </div>
                <div class="entry-details">
                  <p class="detail-line">[学业表现，如：GPA X.X/X（专业前X%）]</p>
                  <p class="detail-courses">[主修课程：课程1、课程2、课程3、课程4、课程5、课程6、课程7、课程8...]</p>
                </div>
              </div>
            </div>
          </section>
          
          <section class="section-pro">
            <div class="section-banner" style="background: ${accentColor};">
              <h3>工作经验</h3>
            </div>
            <div class="section-content">
              <div class="entry-item">
                <div class="entry-header">
                  <span class="entry-date">[起始日期 E] ～ [结束日期 F]</span>
                  <span class="entry-title">[公司名称]</span>
                  <span class="entry-subtitle">[职位名称]</span>
                </div>
                <div class="entry-details">
                  <p class="detail-line">[工作职责描述1，工作职责描述2，工作职责描述3...]</p>
                </div>
              </div>
              <div class="entry-item">
                <div class="entry-header">
                  <span class="entry-date">[起始日期 G] ～ [结束日期 H]</span>
                  <span class="entry-title">[公司名称]</span>
                  <span class="entry-subtitle">[职位名称]</span>
                </div>
                <div class="entry-details">
                  <p class="detail-line">[工作职责描述1，工作职责描述2，工作职责描述3...]</p>
                </div>
              </div>
            </div>
          </section>
          
          <section class="section-pro">
            <div class="section-banner" style="background: ${accentColor};">
              <h3>技能特长</h3>
            </div>
            <div class="section-content">
              <div class="skills-list">
                <p class="skill-line">
                  <span class="skill-category">[技能类别1]：</span>
                  <span class="skill-desc">[技能描述，如：证书、等级等]</span>
                </p>
                <p class="skill-line">
                  <span class="skill-category">[技能类别2]：</span>
                  <span class="skill-desc">[技能描述，如：软件、水平等]</span>
                </p>
                <p class="skill-line">
                  <span class="skill-category">[技能类别3]：</span>
                  <span class="skill-desc">[技能描述，如：语言、熟练程度等]</span>
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    `,
    'modern-tech': `
      <div class="resume-template tech-a4">
        <div class="tech-header">
          <div class="tech-header-main">
            <h1 class="tech-name">[姓名]</h1>
            <div class="tech-info-block">
              <p class="tech-info-line">
                <span>[求职意向]</span>
                <span class="tech-sep">|</span>
                <span>[地理位置]</span>
                <span class="tech-sep">|</span>
                <span>[薪资范围]</span>
                <span class="tech-sep">|</span>
                <span>[状态]</span>
              </p>
              <p class="tech-info-line">
                <span>[年龄]</span>
                <span class="tech-sep">|</span>
                <span>[性别]</span>
                <span class="tech-sep">|</span>
                <span>[工作经验]</span>
                <span class="tech-sep">|</span>
                <span>[身份]</span>
              </p>
              <p class="tech-info-line">
                <span>[电话号码]</span>
                <span class="tech-sep">|</span>
                <span>[电子邮件]</span>
              </p>
            </div>
          </div>
          <div class="tech-avatar">
            <svg viewBox="0 0 100 100" class="tech-avatar-svg">
              <circle cx="50" cy="35" r="25" fill="#f5d0c5"/>
              <ellipse cx="50" cy="90" rx="35" ry="25" fill="#1f2937"/>
              <rect x="35" y="55" width="30" height="20" fill="#ffffff" rx="2"/>
              <path d="M 40 75 L 50 85 L 60 75" fill="#dc2626"/>
              <circle cx="42" cy="32" r="3" fill="#1f2937"/>
              <circle cx="58" cy="32" r="3" fill="#1f2937"/>
              <rect x="38" y="28" width="8" height="6" fill="none" stroke="#1f2937" stroke-width="1.5" rx="1"/>
              <rect x="54" y="28" width="8" height="6" fill="none" stroke="#1f2937" stroke-width="1.5" rx="1"/>
              <path d="M 46 28 L 46 34 M 54 28 L 54 34" stroke="#1f2937" stroke-width="1"/>
              <path d="M 35 20 Q 50 10 65 20" fill="#4a3728"/>
              <path d="M 35 20 Q 50 25 65 20" fill="#4a3728"/>
            </svg>
          </div>
        </div>
        
        <div class="tech-body">
          <section class="tech-section">
            <div class="tech-banner" style="background: ${accentColor};">
              <h3>教育背景</h3>
            </div>
            <div class="tech-content">
              <div class="tech-entry">
                <div class="tech-entry-header">
                  <span class="tech-degree">[高级学位]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-date">[起始日期 A] ～ [结束日期 B]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-school">[大学名称 A]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-major">[专业及学位] ([学位等级 A])</span>
                </div>
                <div class="tech-entry-detail">
                  <p class="tech-detail-line"><span class="tech-detail-label">专业成绩：</span>GPA X.X/4 (前 X%)</p>
                  <p class="tech-detail-line"><span class="tech-detail-label">主修课程：</span>[课程1]、[课程2]、[课程3]、[课程4]、[课程5]、[课程6]、[课程7]、[课程8]...</p>
                </div>
              </div>
              <div class="tech-entry">
                <div class="tech-entry-header">
                  <span class="tech-degree">[低级学位]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-date">[起始日期 B] ～ [结束日期 C]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-school">[大学名称 B]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-major">[专业及学位] ([学位等级 B])</span>
                </div>
              </div>
            </div>
          </section>
          
          <section class="tech-section">
            <div class="tech-banner" style="background: ${accentColor};">
              <h3>工作经验</h3>
            </div>
            <div class="tech-content">
              <div class="tech-entry">
                <div class="tech-entry-header">
                  <span class="tech-position">[职位 A]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-date">[起始日期 C] ～ [结束日期 D]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-company">[公司名称 A]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-job-title">[工作职位]</span>
                </div>
                <div class="tech-entry-detail">
                  <p class="tech-detail-text">负责公司网站的开发和维护，负责公司产品的开发和维护，参与项目需求分析与技术方案设计。</p>
                </div>
              </div>
              <div class="tech-entry">
                <div class="tech-entry-header">
                  <span class="tech-position">[职位 B]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-date">[起始日期 D] ～ [结束日期 E]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-company">[公司名称 B]</span>
                  <span class="tech-sep">|</span>
                  <span class="tech-job-title">[工作职位]</span>
                </div>
                <div class="tech-entry-detail">
                  <p class="tech-detail-text">负责公司网站的开发和维护，负责公司产品的开发和维护，协助团队完成项目交付。</p>
                </div>
              </div>
            </div>
          </section>
          
          <section class="tech-section">
            <div class="tech-banner" style="background: ${accentColor};">
              <h3>技能特长</h3>
            </div>
            <div class="tech-content">
              <div class="tech-skill-item">
                <span class="tech-skill-category">[技能类别 1]：</span>
                <span class="tech-skill-desc">[英语六级]、[竞赛一等奖]、具备良好的英语听说读写能力，能够进行日常交流和专业文档阅读。</span>
              </div>
              <div class="tech-skill-item">
                <span class="tech-skill-category">[技能类别 2]：</span>
                <span class="tech-skill-desc">[计算机二级]、熟练使用Windows平台，掌握Word、Excel、PowerPoint等办公软件，具备良好的文档处理能力。</span>
              </div>
            </div>
          </section>
        </div>
      </div>
    `,
    'creative-design': `
      <div class="resume-template creative">
        <div class="resume-banner" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
          <div class="banner-content">
            <div class="banner-left">
              <h1 class="banner-title-cn">个人简历</h1>
              <p class="banner-title-en">Personal Resume</p>
              <p class="banner-slogan">创意无限可能</p>
              <div class="banner-icons">
                <span class="icon-gold">🎨</span>
                <span class="icon-gold">✨</span>
              </div>
            </div>
            <div class="banner-right">
              <div class="avatar-circle">
                <span>👩‍🎨</span>
              </div>
            </div>
          </div>
          <div class="banner-accent"></div>
        </div>
        <div class="resume-body-modern">
          <section class="resume-section-modern">
            <div class="section-block" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
              <span class="block-pattern"></span>
              <h3>关于我</h3>
            </div>
            <div class="section-grid">
              <div class="grid-item"><span class="label">姓名：</span><span class="value">王五</span></div>
              <div class="grid-item"><span class="label">职位：</span><span class="value">UI/UX 设计师</span></div>
              <div class="grid-item"><span class="label">经验：</span><span class="value">5年</span></div>
              <div class="grid-item"><span class="label">电话：</span><span class="value">137-0000-0000</span></div>
              <div class="grid-item"><span class="label">邮箱：</span><span class="value">wangwu@email.com</span></div>
              <div class="grid-item"><span class="label">作品集：</span><span class="value">wangwu.design</span></div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
              <span class="block-pattern"></span>
              <h3>设计技能</h3>
            </div>
            <div class="skill-bars">
              <div class="skill-bar-item">
                <span class="skill-name">Figma</span>
                <div class="skill-bar"><div class="skill-fill" style="width: 95%;"></div></div>
              </div>
              <div class="skill-bar-item">
                <span class="skill-name">Sketch</span>
                <div class="skill-bar"><div class="skill-fill" style="width: 90%;"></div></div>
              </div>
              <div class="skill-bar-item">
                <span class="skill-name">Adobe XD</span>
                <div class="skill-bar"><div class="skill-fill" style="width: 85%;"></div></div>
              </div>
              <div class="skill-bar-item">
                <span class="skill-name">After Effects</span>
                <div class="skill-bar"><div class="skill-fill" style="width: 80%;"></div></div>
              </div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
              <span class="block-pattern"></span>
              <h3>工作经历</h3>
            </div>
            <div class="work-item-modern">
              <div class="work-header-modern">
                <span class="company-name">网易</span>
                <span class="work-time">2020 - 至今</span>
              </div>
              <div class="work-position">高级UI设计师</div>
              <ul class="work-achievements">
                <li>主导网易云音乐App改版设计</li>
                <li>建立设计规范体系，提升团队协作效率</li>
              </ul>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
              <span class="block-pattern"></span>
              <h3>作品集</h3>
            </div>
            <div class="portfolio-grid">
              <div class="portfolio-item">🎵 音乐App设计</div>
              <div class="portfolio-item">🛒 电商小程序</div>
              <div class="portfolio-item">💰 金融Dashboard</div>
            </div>
          </section>
        </div>
      </div>
    `,
    'minimal-clean': `
      <div class="resume-template minimal-a4">
        <div class="minimal-header">
          <div class="minimal-header-content">
            <h1 class="minimal-name">[姓名]</h1>
            <div class="minimal-info-lines">
              <p class="minimal-info-row">
                <span>[目标岗位]</span>
                <span class="minimal-pipe">|</span>
                <span>[目标城市]</span>
                <span class="minimal-pipe">|</span>
                <span>[期望薪资]</span>
                <span class="minimal-pipe">|</span>
                <span>[到岗状态]</span>
              </p>
              <p class="minimal-info-row">
                <span>[年龄]</span>
                <span class="minimal-pipe">|</span>
                <span>[性别]</span>
                <span class="minimal-pipe">|</span>
                <span>[经验年限]</span>
                <span class="minimal-pipe">|</span>
                <span>[身份面貌]</span>
              </p>
              <p class="minimal-info-row">
                <span>[联系电话]</span>
                <span class="minimal-pipe">|</span>
                <span>[电子邮箱]</span>
              </p>
            </div>
          </div>
          <div class="minimal-avatar">
            <svg viewBox="0 0 100 100" class="minimal-avatar-svg">
              <circle cx="50" cy="35" r="25" fill="#f5d0c5"/>
              <ellipse cx="50" cy="90" rx="35" ry="25" fill="#374151"/>
              <rect x="35" y="55" width="30" height="20" fill="#ffffff" rx="2"/>
              <path d="M 40 75 L 50 85 L 60 75" fill="#dc2626"/>
              <circle cx="42" cy="32" r="3" fill="#1f2937"/>
              <circle cx="58" cy="32" r="3" fill="#1f2937"/>
              <rect x="38" y="28" width="8" height="6" fill="none" stroke="#1f2937" stroke-width="1.5" rx="1"/>
              <rect x="54" y="28" width="8" height="6" fill="none" stroke="#1f2937" stroke-width="1.5" rx="1"/>
              <path d="M 46 28 L 46 34 M 54 28 L 54 34" stroke="#1f2937" stroke-width="1"/>
              <path d="M 35 20 Q 50 10 65 20" fill="#4a3728"/>
              <path d="M 35 20 Q 50 25 65 20" fill="#4a3728"/>
            </svg>
          </div>
        </div>
        
        <div class="minimal-body">
          <section class="minimal-section">
            <h2 class="minimal-section-title">教育经历</h2>
            <div class="minimal-divider"></div>
            <div class="minimal-entry">
              <div class="minimal-entry-header">
                <span class="minimal-entry-title">[学校名称] -- [专业及学历]</span>
                <span class="minimal-entry-date">[开始年份-月份] ～ [结束年份-月份/至今]</span>
              </div>
              <div class="minimal-entry-detail">
                <p class="minimal-detail-line">专业成绩：[成绩描述]</p>
                <p class="minimal-detail-line">主修课程：[课程1]、[课程2]、[课程3]、[课程4]、[课程5]、[课程6]、[课程7]、[课程8]...</p>
              </div>
            </div>
            <div class="minimal-entry">
              <div class="minimal-entry-header">
                <span class="minimal-entry-title">[学校名称] -- [专业及学历]</span>
                <span class="minimal-entry-date">[开始年份-月份] ～ [结束年份-月份]</span>
              </div>
            </div>
          </section>
          
          <section class="minimal-section">
            <h2 class="minimal-section-title">工作经验</h2>
            <div class="minimal-divider"></div>
            <div class="minimal-entry">
              <div class="minimal-entry-header">
                <span class="minimal-entry-title">[公司名称] -- [担任职务]</span>
                <span class="minimal-entry-date">[时间范围]</span>
              </div>
              <div class="minimal-entry-detail">
                <p class="minimal-detail-text">负责公司业务拓展和客户关系维护，参与项目策划与执行，协助团队完成年度目标。主导多个重点项目，实现业务增长。</p>
              </div>
            </div>
            <div class="minimal-entry">
              <div class="minimal-entry-header">
                <span class="minimal-entry-title">[公司名称] -- [担任职务]</span>
                <span class="minimal-entry-date">[时间范围]</span>
              </div>
              <div class="minimal-entry-detail">
                <p class="minimal-detail-text">负责日常运营管理工作，协调各部门资源，优化业务流程，提升团队效率。</p>
              </div>
            </div>
          </section>
          
          <section class="minimal-section">
            <h2 class="minimal-section-title">技能特长</h2>
            <div class="minimal-divider"></div>
            <div class="minimal-skills">
              <p class="minimal-skill-line">[语言能力]：[英语六级]、[日语N2]，具备良好的听说读写能力</p>
              <p class="minimal-skill-line">[计算机技能]：[计算机二级]、熟练使用Office办公软件、Photoshop等</p>
              <p class="minimal-skill-line">[专业证书]：[相关职业资格证书名称]</p>
            </div>
          </section>
          
          <section class="minimal-section">
            <h2 class="minimal-section-title">自我评价</h2>
            <div class="minimal-divider"></div>
            <p class="minimal-evaluation">
              本人具有扎实的专业基础和丰富的实践经验，<span class="minimal-highlight">具备优秀的团队协作能力</span>，善于沟通协调，责任心强。在工作中注重细节，追求卓越，能够快速适应新环境并承担挑战性任务。具有良好的学习能力和创新思维，期待在新的岗位上发挥所长，为公司发展贡献力量。
            </p>
          </section>
          
          <section class="minimal-section">
            <h2 class="minimal-section-title">项目经历</h2>
            <div class="minimal-divider"></div>
            <div class="minimal-entry">
              <div class="minimal-entry-header">
                <span class="minimal-entry-title">[项目名称] -- [项目角色]</span>
                <span class="minimal-entry-date">[时间范围]</span>
              </div>
              <div class="minimal-entry-detail">
                <p class="minimal-detail-text">负责项目的整体规划与执行，协调各方资源，确保项目按时交付。参与需求分析、方案设计及后期优化工作。</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    `,
    'elegant': `
      <div class="resume-template elegant">
        <div class="resume-banner" style="background: linear-gradient(135deg, ${accentColor}, #d97706);">
          <div class="banner-content">
            <div class="banner-left">
              <h1 class="banner-title-cn">个人简历</h1>
              <p class="banner-title-en">Personal Resume</p>
              <p class="banner-slogan">追求卓越品质</p>
              <div class="banner-icons">
                <span class="icon-gold">👔</span>
                <span class="icon-gold">📊</span>
              </div>
            </div>
            <div class="banner-right">
              <div class="avatar-circle">
                <span>👨‍💼</span>
              </div>
            </div>
          </div>
          <div class="banner-accent"></div>
        </div>
        <div class="resume-body-modern">
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>基本信息</h3>
            </div>
            <div class="section-grid">
              <div class="grid-item"><span class="label">姓名：</span><span class="value">孙七</span></div>
              <div class="grid-item"><span class="label">职位：</span><span class="value">管理咨询顾问</span></div>
              <div class="grid-item"><span class="label">电话：</span><span class="value">136-0000-0000</span></div>
              <div class="grid-item"><span class="label">邮箱：</span><span class="value">sunqi@email.com</span></div>
              <div class="grid-item"><span class="label">地点：</span><span class="value">北京市</span></div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>教育背景</h3>
            </div>
            <div class="edu-item-modern">
              <div class="edu-header">
                <span class="school-name">清华大学</span>
                <span class="edu-time">2018 - 2020</span>
              </div>
              <div class="edu-detail">
                <span>MBA · 硕士</span>
              </div>
            </div>
            <div class="edu-item-modern">
              <div class="edu-header">
                <span class="school-name">中国人民大学</span>
                <span class="edu-time">2012 - 2016</span>
              </div>
              <div class="edu-detail">
                <span>经济学 · 本科</span>
              </div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>工作经历</h3>
            </div>
            <div class="work-item-modern">
              <div class="work-header-modern">
                <span class="company-name">麦肯锡咨询</span>
                <span class="work-time">2020 - 至今</span>
              </div>
              <div class="work-position">咨询顾问</div>
              <ul class="work-achievements">
                <li>主导10+战略咨询项目，覆盖金融、零售、科技行业</li>
                <li>帮助客户实现年均20%+的业务增长</li>
              </ul>
            </div>
            <div class="work-item-modern">
              <div class="work-header-modern">
                <span class="company-name">德勤咨询</span>
                <span class="work-time">2016 - 2018</span>
              </div>
              <div class="work-position">分析师</div>
              <ul class="work-achievements">
                <li>参与数字化转型项目，服务世界500强客户</li>
              </ul>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>核心技能</h3>
            </div>
            <div class="skill-tags-modern">
              <span class="skill-tag-modern">战略规划</span>
              <span class="skill-tag-modern">商业分析</span>
              <span class="skill-tag-modern">项目管理</span>
              <span class="skill-tag-modern">团队领导</span>
            </div>
          </section>
        </div>
      </div>
    `,
    'startup': `
      <div class="resume-template startup-a4">
        <div class="startup-header">
          <div class="startup-header-bg"></div>
          <div class="startup-header-content">
            <div class="startup-left">
              <h1 class="startup-name">[姓名]</h1>
              <p class="startup-intention">
                <span>[目标岗位]</span>
                <span class="startup-pipe">|</span>
                <span>[目标城市]</span>
                <span class="startup-pipe">|</span>
                <span>[期望薪资]</span>
                <span class="startup-pipe">|</span>
                <span>[到岗状态]</span>
              </p>
              <div class="startup-grid">
                <div class="startup-grid-item">
                  <span class="startup-icon">👤</span>
                  <span class="startup-label">年龄</span>
                  <span class="startup-value">[具体年龄]</span>
                </div>
                <div class="startup-grid-item">
                  <span class="startup-icon">⚧</span>
                  <span class="startup-label">性别</span>
                  <span class="startup-value">[具体性别]</span>
                </div>
                <div class="startup-grid-item">
                  <span class="startup-icon">💼</span>
                  <span class="startup-label">工作年限</span>
                  <span class="startup-value">[经验年限]</span>
                </div>
                <div class="startup-grid-item">
                  <span class="startup-icon">📞</span>
                  <span class="startup-label">电话</span>
                  <span class="startup-value">[联系电话]</span>
                </div>
                <div class="startup-grid-item">
                  <span class="startup-icon">📧</span>
                  <span class="startup-label">邮箱</span>
                  <span class="startup-value">[电子邮箱]</span>
                </div>
                <div class="startup-grid-item">
                  <span class="startup-icon">🏛️</span>
                  <span class="startup-label">政治面貌</span>
                  <span class="startup-value">[身份状态]</span>
                </div>
              </div>
            </div>
            <div class="startup-right">
              <div class="startup-avatar">
                <svg viewBox="0 0 100 100" class="startup-avatar-svg">
                  <circle cx="50" cy="35" r="25" fill="#f5d0c5"/>
                  <ellipse cx="50" cy="90" rx="35" ry="25" fill="#374151"/>
                  <rect x="35" y="55" width="30" height="20" fill="#ffffff" rx="2"/>
                  <path d="M 40 75 L 50 85 L 60 75" fill="#dc2626"/>
                  <circle cx="42" cy="32" r="3" fill="#1f2937"/>
                  <circle cx="58" cy="32" r="3" fill="#1f2937"/>
                  <rect x="38" y="28" width="8" height="6" fill="none" stroke="#1f2937" stroke-width="1.5" rx="1"/>
                  <rect x="54" y="28" width="8" height="6" fill="none" stroke="#1f2937" stroke-width="1.5" rx="1"/>
                  <path d="M 46 28 L 46 34 M 54 28 L 54 34" stroke="#1f2937" stroke-width="1"/>
                  <path d="M 35 20 Q 50 10 65 20" fill="#4a3728"/>
                  <path d="M 35 20 Q 50 25 65 20" fill="#4a3728"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
        
        <div class="startup-body">
          <section class="startup-section">
            <h2 class="startup-section-title">教育背景</h2>
            <div class="startup-divider"></div>
            <div class="startup-entry">
              <div class="startup-entry-header">
                <span class="startup-entry-title">[学校名称] -- [专业及学历]</span>
                <span class="startup-entry-date">[开始时间] ～ [结束时间]</span>
              </div>
              <div class="startup-entry-detail">
                <p class="startup-detail-line"><span class="startup-detail-label">专业成绩：</span>[成绩描述]</p>
                <p class="startup-detail-line"><span class="startup-detail-label">主修课程：</span>[课程1]、[课程2]、[课程3]、[课程4]、[课程5]、[课程6]、[课程7]、[课程8]...</p>
              </div>
            </div>
          </section>
          
          <section class="startup-section">
            <h2 class="startup-section-title">工作经验</h2>
            <div class="startup-divider"></div>
            <div class="startup-entry">
              <div class="startup-entry-header">
                <span class="startup-entry-title">[公司名称] -- [担任职务]</span>
                <span class="startup-entry-date">[时间范围]</span>
              </div>
              <div class="startup-entry-detail">
                <p class="startup-detail-text">负责公司核心业务系统的开发与维护，参与技术架构设计，带领团队完成多个重要项目交付。</p>
                <p class="startup-detail-text">主导产品迭代优化，提升用户体验，实现业务指标持续增长。</p>
              </div>
            </div>
            <div class="startup-entry">
              <div class="startup-entry-header">
                <span class="startup-entry-title">[公司名称] -- [担任职务]</span>
                <span class="startup-entry-date">[时间范围]</span>
              </div>
              <div class="startup-entry-detail">
                <p class="startup-detail-text">参与项目需求分析与技术方案设计，负责核心模块开发，确保项目按时高质量交付。</p>
              </div>
            </div>
          </section>
          
          <section class="startup-section">
            <h2 class="startup-section-title">技能特长</h2>
            <div class="startup-divider"></div>
            <div class="startup-skills">
              <p class="startup-skill-line"><span class="startup-skill-label">[编程语言]：</span>[Java]、[Python]、[JavaScript]，熟练掌握多种开发语言</p>
              <p class="startup-skill-line"><span class="startup-skill-label">[框架技术]：</span>[Spring Boot]、[Vue.js]、[React]，具备全栈开发能力</p>
              <p class="startup-skill-line"><span class="startup-skill-label">[专业证书]：</span>[相关职业资格证书名称]</p>
            </div>
          </section>
          
          <section class="startup-section">
            <h2 class="startup-section-title">自我评价</h2>
            <div class="startup-divider"></div>
            <p class="startup-evaluation">
              本人具有扎实的专业基础和丰富的项目经验，<span class="startup-highlight">具备优秀的团队协作能力</span>，善于沟通协调，责任心强。在工作中注重细节，追求卓越，能够快速适应新环境并承担挑战性任务。具有良好的学习能力和创新思维，期待在新的岗位上发挥所长，为公司发展贡献力量。
            </p>
          </section>
          
          <section class="startup-section">
            <h2 class="startup-section-title">项目经历</h2>
            <div class="startup-divider"></div>
            <div class="startup-entry">
              <div class="startup-entry-header">
                <span class="startup-entry-title">[项目名称] -- [项目角色]</span>
                <span class="startup-entry-date">[时间范围]</span>
              </div>
              <div class="startup-entry-detail">
                <p class="startup-detail-text">负责项目的整体规划与执行，协调各方资源，确保项目按时交付。参与需求分析、方案设计及后期优化工作，项目取得良好成效。</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    `,
    'modern-minimal': `
      <div class="resume-template modern-minimal">
        <div class="resume-banner" style="background: linear-gradient(135deg, ${accentColor}, #a78bfa);">
          <div class="banner-content">
            <div class="banner-left">
              <h1 class="banner-title-cn">个人简历</h1>
              <p class="banner-title-en">Personal Resume</p>
              <p class="banner-slogan">细心从每一个细节开始</p>
              <div class="banner-icons">
                <span class="icon-gold">🌿</span>
                <span class="icon-gold">✉️</span>
              </div>
            </div>
            <div class="banner-right">
              <div class="avatar-placeholder">
                <div class="avatar-circle">
                  <span>👤</span>
                </div>
              </div>
            </div>
          </div>
          <div class="banner-accent"></div>
        </div>
        <div class="resume-body-modern">
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>基本信息</h3>
            </div>
            <div class="section-grid">
              <div class="grid-item"><span class="label">姓名：</span><span class="value">张三</span></div>
              <div class="grid-item"><span class="label">性别：</span><span class="value">男</span></div>
              <div class="grid-item"><span class="label">电话：</span><span class="value">138-0000-0000</span></div>
              <div class="grid-item"><span class="label">年龄：</span><span class="value">28岁</span></div>
              <div class="grid-item"><span class="label">经验：</span><span class="value">5年</span></div>
              <div class="grid-item"><span class="label">邮箱：</span><span class="value">zhangsan@email.com</span></div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>求职意向</h3>
            </div>
            <div class="section-grid">
              <div class="grid-item"><span class="label">期望职位：</span><span class="value">产品经理</span></div>
              <div class="grid-item"><span class="label">期望城市：</span><span class="value">北京</span></div>
              <div class="grid-item"><span class="label">期望薪资：</span><span class="value">面议</span></div>
              <div class="grid-item"><span class="label">到岗时间：</span><span class="value">随时</span></div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>教育背景</h3>
            </div>
            <div class="edu-item-modern">
              <div class="edu-header">
                <span class="school-name">北京大学</span>
                <span class="edu-time">2016.09 - 2020.06</span>
              </div>
              <div class="edu-detail">
                <span>计算机科学与技术 · 本科</span>
              </div>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>工作经验</h3>
            </div>
            <div class="work-item-modern">
              <div class="work-header-modern">
                <span class="company-name">字节跳动</span>
                <span class="work-time">2020.07 - 至今</span>
              </div>
              <div class="work-position">高级产品经理</div>
              <ul class="work-achievements">
                <li>负责抖音电商产品规划，DAU从500万增长至2000万</li>
                <li>搭建商家后台系统，提升商家运营效率40%</li>
              </ul>
            </div>
          </section>
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>技能特长</h3>
            </div>
            <div class="skill-tags-modern">
              <span class="skill-tag-modern">产品规划</span>
              <span class="skill-tag-modern">用户增长</span>
              <span class="skill-tag-modern">数据分析</span>
              <span class="skill-tag-modern">团队管理</span>
            </div>
          </section>
        </div>
      </div>
    `
  };
  
  return templates[id] || templates['minimal-clean'];
};

const getMiniPreviewHtml = (id: string, accentColor: string): string => {
  const miniTemplates: Record<string, string> = {
    'executive': `
      <div class="mini-header-pro" style="background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);">
        <div class="mini-name-pro">姓名</div>
        <div class="mini-info-line">求职意向：[目标岗位]</div>
        <div class="mini-info-line">基本信息：[年龄]岁 | [性别]</div>
      </div>
      <div class="mini-body-pro">
        <div class="mini-banner" style="background: ${accentColor};">教育背景</div>
        <div class="mini-entry">
          <div class="mini-entry-row">[日期] | [学校] | [专业]</div>
        </div>
        <div class="mini-banner" style="background: ${accentColor};">工作经验</div>
        <div class="mini-entry">
          <div class="mini-entry-row">[日期] | [公司] | [职位]</div>
        </div>
        <div class="mini-banner" style="background: ${accentColor};">技能特长</div>
        <div class="mini-entry">
          <div class="mini-entry-row">[技能]: [描述]</div>
        </div>
      </div>
    `,
    'modern-tech': `
      <div class="mini-tech-header">
        <div class="mini-tech-name">[姓名]</div>
        <div class="mini-tech-info">[求职意向] | [地点] | [薪资]</div>
        <div class="mini-tech-info">[年龄] | [性别] | [经验]</div>
      </div>
      <div class="mini-tech-body">
        <div class="mini-tech-banner" style="background: ${accentColor};">教育背景</div>
        <div class="mini-tech-entry">[学位] | [日期] | [学校]</div>
        <div class="mini-tech-banner" style="background: ${accentColor};">工作经验</div>
        <div class="mini-tech-entry">[职位] | [日期] | [公司]</div>
        <div class="mini-tech-banner" style="background: ${accentColor};">技能特长</div>
        <div class="mini-tech-entry">[技能类别]: [描述]</div>
      </div>
    `,
    'creative-design': `
      <div class="mini-header" style="background: linear-gradient(135deg, ${accentColor}, #a855f7);">
        <div class="mini-name">王五</div>
        <div class="mini-title">UI设计师</div>
      </div>
      <div class="mini-body">
        <div class="mini-section">
          <div class="mini-section-title" style="color: ${accentColor};">作品集</div>
          <div class="mini-gallery">
            <div class="mini-gallery-item"></div>
            <div class="mini-gallery-item"></div>
          </div>
        </div>
      </div>
    `,
    'minimal-clean': `
      <div class="mini-minimal-header">
        <div class="mini-minimal-name">[姓名]</div>
        <div class="mini-minimal-info">[目标岗位] | [目标城市] | [期望薪资]</div>
        <div class="mini-minimal-info">[年龄] | [性别] | [经验]</div>
      </div>
      <div class="mini-minimal-body">
        <div class="mini-minimal-section">教育经历</div>
        <div class="mini-minimal-divider"></div>
        <div class="mini-minimal-entry">[学校] -- [专业] | [日期]</div>
        <div class="mini-minimal-section">工作经验</div>
        <div class="mini-minimal-divider"></div>
        <div class="mini-minimal-entry">[公司] -- [职位] | [日期]</div>
        <div class="mini-minimal-section">技能特长</div>
        <div class="mini-minimal-divider"></div>
        <div class="mini-minimal-entry">[技能]: [描述]</div>
      </div>
    `,
    'elegant': `
      <div class="mini-header" style="border-bottom: 2px solid ${accentColor};">
        <div class="mini-name">孙七</div>
        <div class="mini-title">投资经理</div>
      </div>
      <div class="mini-body">
        <div class="mini-section">
          <div class="mini-section-title" style="color: ${accentColor};">工作经历</div>
          <div class="mini-text">中金公司 - 投资经理</div>
        </div>
        <div class="mini-section">
          <div class="mini-section-title" style="color: ${accentColor};">教育背景</div>
          <div class="mini-text">清华经管 MBA</div>
        </div>
      </div>
    `,
    'startup': `
      <div class="mini-startup-wrapper">
        <div class="mini-startup-header">
          <div class="mini-startup-name">[姓名]</div>
          <p class="mini-startup-intention">
            <span>[目标岗位]</span>
            <span class="mini-startup-pipe">|</span>
            <span>[目标城市]</span>
            <span class="mini-startup-pipe">|</span>
            <span>[期望薪资]</span>
          </p>
          <div class="mini-startup-grid">
            <div class="mini-startup-grid-item">
              <span class="mini-startup-icon">👤</span>
              <span>年龄 [具体年龄]</span>
            </div>
            <div class="mini-startup-grid-item">
              <span class="mini-startup-icon">⚧</span>
              <span>性别 [具体性别]</span>
            </div>
            <div class="mini-startup-grid-item">
              <span class="mini-startup-icon">💼</span>
              <span>工作年限 [经验年限]</span>
            </div>
            <div class="mini-startup-grid-item">
              <span class="mini-startup-icon">📞</span>
              <span>电话 [联系电话]</span>
            </div>
          </div>
        </div>
        <div class="mini-startup-body">
          <div class="mini-startup-section">教育背景</div>
          <div class="mini-startup-divider"></div>
          <div class="mini-startup-entry">[学校名称] -- [专业及学历]</div>
          <div class="mini-startup-section">工作经验</div>
          <div class="mini-startup-divider"></div>
          <div class="mini-startup-entry">[公司名称] -- [担任职务]</div>
        </div>
      </div>
    `,
    'modern-minimal': `
      <div class="mini-header-modern" style="background: linear-gradient(135deg, ${accentColor}, #a78bfa);">
        <div class="mini-title-cn">个人简历</div>
        <div class="mini-title-en">Personal Resume</div>
      </div>
      <div class="mini-body">
        <div class="mini-section">
          <div class="mini-section-block" style="background: ${accentColor};">基本信息</div>
          <div class="mini-grid">
            <div class="mini-grid-item">姓名: 张三</div>
            <div class="mini-grid-item">性别: 男</div>
          </div>
        </div>
        <div class="mini-section">
          <div class="mini-section-block" style="background: ${accentColor};">求职意向</div>
          <div class="mini-text">产品经理</div>
        </div>
      </div>
    `,
  };
  
  return miniTemplates[id] || miniTemplates['minimal-clean'];
};

const templates: Template[] = [
  {
    id: 'executive',
    name: '高管专业版',
    description: '适合中高层管理岗位，稳重专业，突出领导力和成就',
    category: 'professional',
    tags: ['管理岗', '商务', '正式'],
    featured: true,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
    accentColor: '#1e3a5f',
    htmlContent: '',
  },
  {
    id: 'modern-tech',
    name: '现代科技',
    description: '适合技术岗位，现代简约，突出技能和项目经验',
    category: 'professional',
    tags: ['技术岗', 'IT', '现代'],
    featured: true,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #f0f9ff 100%)',
    accentColor: '#0369a1',
    htmlContent: '',
  },
  {
    id: 'creative-design',
    name: '创意流程',
    description: '适合设计创意岗位，展现个性与创意思维',
    category: 'creative',
    tags: ['设计岗', '创意', '个性'],
    featured: false,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #fdf4ff 100%)',
    accentColor: '#86198f',
    htmlContent: '',
  },
  {
    id: 'minimal-clean',
    name: '极简清新',
    description: '极简设计，适合各类岗位，干净利落',
    category: 'minimal',
    tags: ['通用', '简约', '清爽'],
    featured: true,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #f9fafb 100%)',
    accentColor: '#374151',
    htmlContent: '',
  },
  {
    id: 'elegant',
    name: '优雅经典',
    description: '优雅精致，适合金融、咨询等专业服务行业',
    category: 'professional',
    tags: ['金融', '咨询', '优雅'],
    featured: false,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #fffbeb 100%)',
    accentColor: '#92400e',
    htmlContent: '',
  },
  {
    id: 'startup',
    name: '创业先锋',
    description: '适合创业公司求职，展现活力与多面能力',
    category: 'creative',
    tags: ['创业', '活力', '全能'],
    featured: false,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #ecfdf5 100%)',
    accentColor: '#047857',
    htmlContent: '',
  },
  {
    id: 'modern-minimal',
    name: '现代简约',
    description: '现代简约风格，深紫金色配色，适合各类专业岗位',
    category: 'professional',
    tags: ['现代', '简约', '专业'],
    featured: true,
    previewBg: 'linear-gradient(180deg, #ffffff 0%, #faf5ff 100%)',
    accentColor: '#7c3aed',
    htmlContent: '',
  },
].map(t => ({
  ...t,
  htmlContent: getTemplateHtml(t.id, t.accentColor)
}));

const activeCategory = ref('all');
const showPreview = ref(false);
const selectedTemplate = ref<Template | null>(null);
const templatePreviewRef = ref<HTMLElement | null>(null);

const emit = defineEmits<{
  selectTemplate: [templateId: string];
}>();

const filteredTemplates = computed(() => {
  if (activeCategory.value === 'all') return templates;
  return templates.filter(t => t.category === activeCategory.value);
});

function previewTemplate(template: Template) {
  selectedTemplate.value = {
    ...template,
    htmlContent: getTemplateHtml(template.id, template.accentColor)
  };
  showPreview.value = true;
}

function useTemplate(template: Template) {
  emit('selectTemplate', template.id);
}

function useSelectedTemplate() {
  if (!selectedTemplate.value) return;
  emit('selectTemplate', selectedTemplate.value.id);
  showPreview.value = false;
}
</script>

<style scoped>
.template-library {
  max-width: 1200px;
  margin: 0 auto;
  animation: fade-up 0.6s ease;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.library-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 32px;
}

.library-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.library-subtitle {
  font-size: 15px;
  color: var(--slate-400);
  max-width: 500px;
  line-height: 1.6;
}

.header-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 20px 32px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  position: relative;
  overflow: hidden;
}

.stat-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.05) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.stat-item:hover::before {
  opacity: 1;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--emerald-400), var(--teal-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
}

.stat-text {
  font-size: 13px;
  color: var(--slate-400);
  margin-top: 4px;
}

.template-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  flex-wrap: wrap;
  padding: 4px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
}

.filter-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn:hover {
  color: var(--white);
  background: var(--white-alpha-5);
}

.filter-btn.active {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  font-weight: 600;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 48px;
}

.template-card {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: all var(--transition-normal);
  position: relative;
}

.template-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-xl);
  padding: 1px;
  background: linear-gradient(135deg, transparent, rgba(16, 185, 129, 0.2), transparent);
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-normal);
}

.template-card:hover {
  transform: translateY(-4px);
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 40px rgba(16, 185, 129, 0.15);
}

.template-card:hover::before {
  opacity: 1;
}

.template-card.featured {
  border-color: rgba(16, 185, 129, 0.2);
}

.template-card.featured::before {
  opacity: 1;
}

.card-preview {
  position: relative;
  height: 220px;
  padding: 24px;
  background: linear-gradient(135deg, var(--bg-tertiary) 0%, rgba(16, 185, 129, 0.05) 100%);
  overflow: hidden;
}

.card-preview::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(16, 185, 129, 0.1) 0%,
    transparent 70%
  );
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-normal);
}

.template-card:hover .card-preview::before {
  opacity: 1;
}

.preview-paper {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-lg);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  overflow: hidden;
  background: var(--bg-secondary);
  transition: all var(--transition-normal);
}

.template-card:hover .preview-paper {
  transform: scale(1.02);
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(16, 185, 129, 0.2);
}

.template-mini-preview {
  width: 100%;
  height: 100%;
  background: white;
  font-size: 8px;
  line-height: 1.4;
  color: #1f2937;
  overflow: hidden;
}

.mini-header {
  padding: 12px 10px 8px;
  color: white;
}

.mini-name {
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 2px;
  color: inherit;
}

.mini-title {
  font-size: 8px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.mini-contact {
  font-size: 7px;
  opacity: 0.8;
}

.mini-body {
  padding: 8px 10px;
}

.mini-section {
  margin-bottom: 8px;
}

.mini-section-title {
  font-size: 8px;
  font-weight: 600;
  margin-bottom: 3px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mini-text {
  font-size: 7px;
  color: #4b5563;
  line-height: 1.4;
}

.mini-tags {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
}

.mini-tag {
  padding: 2px 5px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 3px;
  font-size: 6px;
  font-weight: 500;
  color: #059669;
}

.mini-gallery {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
}

.mini-gallery-item {
  height: 20px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border-radius: 2px;
}

.mini-header-modern {
  padding: 10px 8px;
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  color: white;
}

.mini-title-cn {
  font-size: 10px;
  font-weight: 700;
  margin-bottom: 2px;
}

.mini-title-en {
  font-size: 6px;
  opacity: 0.9;
}

.mini-section-block {
  padding: 3px 6px;
  color: white;
  font-size: 6px;
  font-weight: 600;
  border-radius: 2px;
  margin-bottom: 4px;
}

.mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
}

.mini-grid-item {
  font-size: 5px;
  color: #4b5563;
}

.mini-header-pro {
  padding: 10px 8px;
  border-bottom: 1px solid #e5e7eb;
}

.mini-name-pro {
  font-size: 12px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 4px;
}

.mini-info-line {
  font-size: 6px;
  color: #6b7280;
  margin-bottom: 2px;
}

.mini-body-pro {
  padding: 6px 8px;
}

.mini-banner {
  padding: 3px 6px;
  color: white;
  font-size: 6px;
  font-weight: 700;
  border-radius: 2px;
  margin-bottom: 4px;
}

.mini-entry {
  margin-bottom: 6px;
}

.mini-entry-row {
  font-size: 5px;
  color: #4b5563;
  line-height: 1.4;
}

.mini-tech-header {
  padding: 10px 8px;
  text-align: center;
  border-bottom: 1px solid #e5e7eb;
}

.mini-tech-name {
  font-size: 11px;
  font-weight: 800;
  color: #1f2937;
  margin-bottom: 4px;
}

.mini-tech-info {
  font-size: 6px;
  color: #6b7280;
  margin-bottom: 2px;
}

.mini-tech-body {
  padding: 6px 8px;
}

.mini-tech-banner {
  padding: 3px 6px;
  color: white;
  font-size: 6px;
  font-weight: 700;
  border-radius: 2px;
  margin-bottom: 4px;
}

.mini-tech-entry {
  font-size: 5px;
  color: #4b5563;
  margin-bottom: 4px;
  line-height: 1.4;
}

.mini-minimal-header {
  padding: 10px 8px;
  text-align: center;
}

.mini-minimal-name {
  font-size: 11px;
  font-weight: 800;
  color: #000000;
  margin-bottom: 4px;
}

.mini-minimal-info {
  font-size: 6px;
  color: #000000;
  margin-bottom: 2px;
}

.mini-minimal-body {
  padding: 6px 8px;
}

.mini-minimal-section {
  font-size: 7px;
  font-weight: 700;
  color: #000000;
  margin-bottom: 2px;
}

.mini-minimal-divider {
  height: 1px;
  background: #000000;
  margin-bottom: 4px;
}

.mini-minimal-entry {
  font-size: 5px;
  color: #000000;
  margin-bottom: 6px;
  line-height: 1.4;
}

.mini-startup-wrapper {
  width: 100%;
  height: 100%;
  background: white;
}

.mini-startup-header {
  background: #0d9488;
  padding: 8px 10px 10px 10px;
}

.mini-startup-name {
  font-size: 11px;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 4px;
  letter-spacing: 1px;
}

.mini-startup-intention {
  font-size: 6px;
  color: #ffffff;
  margin: 0 0 6px 0;
  opacity: 0.95;
}

.mini-startup-pipe {
  margin: 0 4px;
  opacity: 0.6;
}

.mini-startup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3px 8px;
}

.mini-startup-grid-item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 5px;
  color: #ffffff;
}

.mini-startup-icon {
  font-size: 6px;
}

.mini-startup-body {
  padding: 6px 10px;
}

.mini-startup-section {
  font-size: 6px;
  font-weight: 700;
  color: #0d9488;
  margin-bottom: 2px;
  letter-spacing: 0.5px;
}

.mini-startup-divider {
  height: 1px;
  background: #0d9488;
  margin-bottom: 4px;
}

.mini-startup-entry {
  font-size: 5px;
  color: #374151;
  margin-bottom: 6px;
  line-height: 1.4;
}

.paper-line.title {
  width: 60%;
  height: 12px;
  margin-bottom: 12px;
}

.paper-line.short {
  width: 40%;
}

.paper-line.medium {
  width: 80%;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: linear-gradient(
    180deg,
    rgba(9, 9, 11, 0.4) 0%,
    rgba(9, 9, 11, 0.8) 100%
  );
  backdrop-filter: blur(8px);
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-normal);
  padding: 20px;
}

.template-card:hover .preview-overlay {
  opacity: 1;
  pointer-events: auto;
}

.preview-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  max-width: 200px;
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-xl);
  font-size: 14px;
  font-weight: 600;
  color: var(--bg-primary);
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
  transition: all var(--transition-normal);
  pointer-events: auto;
  position: relative;
  overflow: hidden;
}

.preview-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.preview-btn svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.preview-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
}

.preview-btn:hover::before {
  opacity: 1;
}

.preview-btn:active {
  transform: translateY(0);
}

.card-info {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--white);
}

.featured-badge {
  padding: 4px 10px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-radius: var(--radius-md);
  font-size: 11px;
  font-weight: 600;
  color: var(--bg-primary);
}

.card-desc {
  font-size: 13px;
  color: var(--slate-400);
  line-height: 1.6;
  margin-bottom: 12px;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  font-size: 11px;
  font-weight: 500;
  color: var(--slate-400);
}

.card-actions {
  display: flex;
  gap: 10px;
  padding: 0 20px 20px;
  position: relative;
  z-index: 2;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  z-index: 1;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn.secondary {
  background: var(--bg-tertiary);
  color: var(--slate-400);
}

.action-btn.secondary:hover {
  background: var(--white-alpha-10);
  color: var(--white);
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
}

.action-btn.full {
  width: 100%;
}

.tips-section {
  margin-top: 48px;
}

.tips-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  background: var(--bg-secondary);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-xl);
  position: relative;
  overflow: hidden;
}

.tips-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
}

.tips-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: var(--radius-lg);
  color: var(--emerald-400);
  flex-shrink: 0;
}

.tips-icon svg {
  width: 24px;
  height: 24px;
}

.tips-content {
  flex: 1;
}

.tips-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 12px;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  color: var(--slate-400);
}

.tips-list li {
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.6;
}

.preview-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(9, 9, 11, 0.8);
  backdrop-filter: blur(8px);
}

.modal-content {
  width: 90%;
  max-width: 600px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: 0 0 60px rgba(16, 185, 129, 0.2);
}

.modal-content.large {
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: var(--border-subtle);
  flex-shrink: 0;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--white);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--bg-tertiary);
  border: none;
  border-radius: var(--radius-md);
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background: var(--white-alpha-10);
  color: var(--white);
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.template-preview-full {
  background: white;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-lg);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: var(--border-subtle);
  background: var(--bg-tertiary);
  flex-shrink: 0;
}

.modal-btn {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-btn.secondary {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  color: var(--slate-400);
}

.modal-btn.secondary:hover {
  background: var(--white-alpha-10);
  color: var(--white);
}

.modal-btn.primary {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.modal-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
}

/* Template Styles */
.template-preview-full :deep(.resume-template) {
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  color: #1f2937;
  line-height: 1.6;
}

.template-preview-full :deep(.resume-header) {
  margin-bottom: 24px;
  padding-bottom: 16px;
}

.template-preview-full :deep(.resume-name) {
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 8px 0;
}

.template-preview-full :deep(.resume-title) {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.template-preview-full :deep(.resume-contact) {
  font-size: 14px;
  color: #6b7280;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.template-preview-full :deep(.resume-section) {
  margin-bottom: 24px;
}

.template-preview-full :deep(.section-title) {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid;
}

.template-preview-full :deep(.work-item) {
  margin-bottom: 16px;
}

.template-preview-full :deep(.work-header) {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.template-preview-full :deep(.company) {
  font-weight: 700;
}

.template-preview-full :deep(.period) {
  color: #6b7280;
  font-size: 14px;
}

.template-preview-full :deep(.position) {
  color: #374151;
  font-size: 14px;
  margin: 4px 0;
}

.template-preview-full :deep(.achievements) {
  margin: 8px 0;
  padding-left: 20px;
  font-size: 14px;
}

.template-preview-full :deep(.achievements li) {
  margin-bottom: 4px;
}

.template-preview-full :deep(.skills) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-preview-full :deep(.skill-tag) {
  padding: 4px 12px;
  background: #f3f4f6;
  border-radius: 4px;
  font-size: 13px;
}

.template-preview-full :deep(.edu-item) {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.template-preview-full :deep(.school) {
  font-weight: 700;
}

.template-preview-full :deep(.divider) {
  height: 3px;
  margin-bottom: 24px;
}

/* Creative Template */
.template-preview-full :deep(.resume-template.creative) {
  display: flex;
  min-height: 400px;
}

.template-preview-full :deep(.resume-template.creative .resume-sidebar) {
  width: 200px;
  padding: 24px;
  color: white;
}

.template-preview-full :deep(.resume-template.creative .resume-main) {
  flex: 1;
  padding: 24px;
}

.template-preview-full :deep(.avatar-placeholder) {
  width: 80px;
  height: 80px;
  background: rgba(255,255,255,0.3);
  border-radius: 50%;
  margin-bottom: 16px;
}

.template-preview-full :deep(.skill-bar) {
  height: 6px;
  background: rgba(255,255,255,0.3);
  border-radius: 3px;
  margin-bottom: 8px;
  position: relative;
}

.template-preview-full :deep(.skill-bar span) {
  display: block;
  height: 100%;
  background: white;
  border-radius: 3px;
}

.template-preview-full :deep(.skill-bar label) {
  position: absolute;
  right: 0;
  top: -18px;
  font-size: 12px;
}

.template-preview-full :deep(.portfolio-grid) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.template-preview-full :deep(.portfolio-item) {
  height: 60px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #6b7280;
}

/* Elegant Template */
.template-preview-full :deep(.resume-template.elegant .two-column) {
  display: flex;
  gap: 32px;
}

.template-preview-full :deep(.resume-template.elegant .column-left) {
  width: 200px;
}

.template-preview-full :deep(.resume-template.elegant .column-right) {
  flex: 1;
}

/* Startup Template */
.template-preview-full :deep(.project-grid) {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.template-preview-full :deep(.project-card) {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.template-preview-full :deep(.project-card h3) {
  margin: 0 0 8px 0;
  font-size: 15px;
}

.template-preview-full :deep(.project-card .tech) {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
}

.template-preview-full :deep(.skill-tags) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-preview-full :deep(.skill-tags span) {
  padding: 6px 14px;
  background: #f3f4f6;
  border-radius: 20px;
  font-size: 13px;
}

/* Tech Stack */
.template-preview-full :deep(.tech-stack) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.template-preview-full :deep(.tech-item) {
  font-size: 14px;
}

/* Modern Minimal Template */
.template-preview-full :deep(.resume-template.modern-minimal) {
  background: white;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
}

.template-preview-full :deep(.resume-banner) {
  padding: 40px;
  color: white;
  position: relative;
  overflow: hidden;
}

.template-preview-full :deep(.banner-content) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-preview-full :deep(.banner-left) {
  flex: 1;
}

.template-preview-full :deep(.banner-title-cn) {
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 8px 0;
  letter-spacing: 4px;
}

.template-preview-full :deep(.banner-title-en) {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.template-preview-full :deep(.banner-slogan) {
  font-size: 14px;
  opacity: 0.8;
  margin: 0 0 16px 0;
}

.template-preview-full :deep(.banner-icons) {
  display: flex;
  gap: 12px;
}

.template-preview-full :deep(.icon-gold) {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.template-preview-full :deep(.banner-right) {
  margin-left: 40px;
}

.template-preview-full :deep(.avatar-circle) {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.template-preview-full :deep(.banner-accent) {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #7c3aed, #fbbf24, #7c3aed);
}

.template-preview-full :deep(.resume-body-modern) {
  padding: 32px 40px;
}

.template-preview-full :deep(.resume-section-modern) {
  margin-bottom: 28px;
}

.template-preview-full :deep(.section-block) {
  padding: 10px 20px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  letter-spacing: 2px;
}

.template-preview-full :deep(.block-pattern) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 3px,
    rgba(255, 255, 255, 0.1) 3px,
    rgba(255, 255, 255, 0.1) 6px
  );
}

.template-preview-full :deep(.section-block h3) {
  margin: 0;
  position: relative;
  z-index: 1;
}

.template-preview-full :deep(.section-grid) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 24px;
}

.template-preview-full :deep(.grid-item) {
  font-size: 14px;
  color: #374151;
}

.template-preview-full :deep(.grid-item .label) {
  color: #6b7280;
  font-weight: 500;
}

.template-preview-full :deep(.grid-item .value) {
  color: #1f2937;
  font-weight: 600;
}

.template-preview-full :deep(.edu-item-modern) {
  margin-bottom: 12px;
}

.template-preview-full :deep(.edu-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.template-preview-full :deep(.school-name) {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.template-preview-full :deep(.edu-time) {
  font-size: 14px;
  color: #6b7280;
}

.template-preview-full :deep(.edu-detail) {
  font-size: 14px;
  color: #4b5563;
}

.template-preview-full :deep(.work-item-modern) {
  margin-bottom: 20px;
}

.template-preview-full :deep(.work-header-modern) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.template-preview-full :deep(.company-name) {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.template-preview-full :deep(.work-time) {
  font-size: 14px;
  color: #6b7280;
}

.template-preview-full :deep(.work-position) {
  font-size: 14px;
  color: #7c3aed;
  font-weight: 600;
  margin-bottom: 8px;
}

.template-preview-full :deep(.work-achievements) {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.8;
}

.template-preview-full :deep(.work-achievements li) {
  margin-bottom: 4px;
}

.template-preview-full :deep(.skill-tags-modern) {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.template-preview-full :deep(.skill-tag-modern) {
  padding: 8px 20px;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  border-left: 3px solid #7c3aed;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

/* Executive Pro Template */
.template-preview-full :deep(.resume-template.executive-pro) {
  background: white;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  padding: 0;
}

.template-preview-full :deep(.resume-header-pro) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 40px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.template-preview-full :deep(.header-left) {
  flex: 1;
}

.template-preview-full :deep(.name-title) {
  font-size: 36px;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 16px 0;
  letter-spacing: 1px;
}

.template-preview-full :deep(.info-lines) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.template-preview-full :deep(.info-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.info-label) {
  color: #6b7280;
  font-weight: 500;
}

.template-preview-full :deep(.separator) {
  color: #d1d5db;
  margin: 0 8px;
}

.template-preview-full :deep(.header-right) {
  margin-left: 32px;
}

.template-preview-full :deep(.avatar-pro) {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-preview-full :deep(.avatar-svg) {
  width: 100%;
  height: 100%;
}

.template-preview-full :deep(.resume-body-pro) {
  padding: 24px 40px;
}

.template-preview-full :deep(.section-pro) {
  margin-bottom: 24px;
}

.template-preview-full :deep(.section-banner) {
  padding: 10px 20px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 16px;
  border-radius: 4px;
  letter-spacing: 1px;
}

.template-preview-full :deep(.section-banner h3) {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.template-preview-full :deep(.section-content) {
  padding: 0 4px;
}

.template-preview-full :deep(.entry-item) {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.template-preview-full :deep(.entry-item:last-child) {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.template-preview-full :deep(.entry-header) {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.template-preview-full :deep(.entry-date) {
  font-size: 13px;
  color: #3b82f6;
  font-weight: 500;
  min-width: 160px;
}

.template-preview-full :deep(.entry-title) {
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
  flex: 1;
}

.template-preview-full :deep(.entry-subtitle) {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.template-preview-full :deep(.entry-details) {
  padding-left: 0;
}

.template-preview-full :deep(.detail-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0 0 6px 0;
  line-height: 1.6;
}

.template-preview-full :deep(.detail-courses) {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.skills-list) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.template-preview-full :deep(.skill-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.skill-category) {
  color: #3b82f6;
  font-weight: 600;
}

.template-preview-full :deep(.skill-desc) {
  color: #4b5563;
}

/* Tech A4 Template */
.template-preview-full :deep(.resume-template.tech-a4) {
  background: white;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  padding: 0;
}

.template-preview-full :deep(.tech-header) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 40px;
  border-bottom: 1px solid #e5e7eb;
  position: relative;
}

.template-preview-full :deep(.tech-header-main) {
  flex: 1;
  text-align: center;
}

.template-preview-full :deep(.tech-name) {
  font-size: 32px;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 16px 0;
  letter-spacing: 2px;
}

.template-preview-full :deep(.tech-info-block) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.template-preview-full :deep(.tech-info-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.tech-sep) {
  color: #d1d5db;
  margin: 0 8px;
}

.template-preview-full :deep(.tech-avatar) {
  position: absolute;
  right: 40px;
  top: 32px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-preview-full :deep(.tech-avatar-svg) {
  width: 100%;
  height: 100%;
}

.template-preview-full :deep(.tech-body) {
  padding: 24px 40px;
}

.template-preview-full :deep(.tech-section) {
  margin-bottom: 20px;
}

.template-preview-full :deep(.tech-banner) {
  padding: 8px 16px;
  color: white;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
  border-radius: 2px;
  letter-spacing: 1px;
}

.template-preview-full :deep(.tech-banner h3) {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
}

.template-preview-full :deep(.tech-content) {
  padding: 0 4px;
}

.template-preview-full :deep(.tech-entry) {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.template-preview-full :deep(.tech-entry:last-child) {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.template-preview-full :deep(.tech-entry-header) {
  font-size: 13px;
  color: #374151;
  margin-bottom: 6px;
  line-height: 1.6;
}

.template-preview-full :deep(.tech-degree),
.template-preview-full :deep(.tech-position) {
  font-weight: 600;
  color: #1f2937;
}

.template-preview-full :deep(.tech-date) {
  color: #0ea5e9;
}

.template-preview-full :deep(.tech-school),
.template-preview-full :deep(.tech-company) {
  font-weight: 600;
}

.template-preview-full :deep(.tech-major),
.template-preview-full :deep(.tech-job-title) {
  color: #6b7280;
}

.template-preview-full :deep(.tech-entry-detail) {
  padding-left: 0;
}

.template-preview-full :deep(.tech-detail-line) {
  font-size: 12px;
  color: #4b5563;
  margin: 0 0 4px 0;
  line-height: 1.6;
}

.template-preview-full :deep(.tech-detail-label) {
  color: #6b7280;
  font-weight: 500;
}

.template-preview-full :deep(.tech-detail-text) {
  font-size: 12px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.tech-skill-item) {
  font-size: 13px;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.6;
}

.template-preview-full :deep(.tech-skill-category) {
  font-weight: 600;
  color: #0ea5e9;
}

.template-preview-full :deep(.tech-skill-desc) {
  color: #4b5563;
}

/* Minimal A4 Template */
.template-preview-full :deep(.resume-template.minimal-a4) {
  background: white;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  padding: 0;
}

.template-preview-full :deep(.minimal-header) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 40px 50px 24px 50px;
  position: relative;
}

.template-preview-full :deep(.minimal-header-content) {
  flex: 1;
  text-align: center;
}

.template-preview-full :deep(.minimal-name) {
  font-size: 36px;
  font-weight: 800;
  color: #000000;
  margin: 0 0 16px 0;
  letter-spacing: 4px;
}

.template-preview-full :deep(.minimal-info-lines) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.template-preview-full :deep(.minimal-info-row) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.minimal-pipe) {
  color: #9ca3af;
  margin: 0 10px;
}

.template-preview-full :deep(.minimal-avatar) {
  position: absolute;
  right: 50px;
  top: 40px;
  width: 85px;
  height: 85px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.template-preview-full :deep(.minimal-avatar-svg) {
  width: 100%;
  height: 100%;
}

.template-preview-full :deep(.minimal-body) {
  padding: 0 50px 40px 50px;
}

.template-preview-full :deep(.minimal-section) {
  margin-bottom: 20px;
}

.template-preview-full :deep(.minimal-section-title) {
  font-size: 15px;
  font-weight: 700;
  color: #000000;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
}

.template-preview-full :deep(.minimal-divider) {
  height: 1px;
  background: #000000;
  margin-bottom: 12px;
  width: 100%;
}

.template-preview-full :deep(.minimal-entry) {
  margin-bottom: 12px;
}

.template-preview-full :deep(.minimal-entry-header) {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.template-preview-full :deep(.minimal-entry-title) {
  font-size: 14px;
  font-weight: 700;
  color: #000000;
}

.template-preview-full :deep(.minimal-entry-date) {
  font-size: 13px;
  color: #000000;
  font-weight: 400;
}

.template-preview-full :deep(.minimal-entry-detail) {
  padding-left: 0;
}

.template-preview-full :deep(.minimal-detail-line) {
  font-size: 13px;
  color: #000000;
  margin: 0 0 4px 0;
  line-height: 1.6;
}

.template-preview-full :deep(.minimal-detail-text) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.8;
}

.template-preview-full :deep(.minimal-skills) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.template-preview-full :deep(.minimal-skill-line) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.minimal-evaluation) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.8;
  text-align: justify;
}

.template-preview-full :deep(.minimal-highlight) {
  color: #dc2626;
  font-weight: 600;
}

/* Startup A4 Template */
.template-preview-full :deep(.resume-template.startup-a4) {
  background: white;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  padding: 0;
  position: relative;
}

.template-preview-full :deep(.startup-header) {
  position: relative;
  background: #0d9488;
}

.template-preview-full :deep(.startup-header-bg) {
  display: none;
}

.template-preview-full :deep(.startup-header-content) {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 50px;
  z-index: 1;
}

.template-preview-full :deep(.startup-left) {
  flex: 1;
}

.template-preview-full :deep(.startup-name) {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
}

.template-preview-full :deep(.startup-intention) {
  font-size: 13px;
  color: #ffffff;
  margin: 0 0 16px 0;
  opacity: 0.95;
}

.template-preview-full :deep(.startup-pipe) {
  margin: 0 8px;
  opacity: 0.6;
}

.template-preview-full :deep(.startup-grid) {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 24px;
}

.template-preview-full :deep(.startup-grid-item) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #ffffff;
}

.template-preview-full :deep(.startup-icon) {
  font-size: 14px;
}

.template-preview-full :deep(.startup-label) {
  opacity: 0.8;
}

.template-preview-full :deep(.startup-value) {
  font-weight: 500;
}

.template-preview-full :deep(.startup-right) {
  margin-left: 24px;
}

.template-preview-full :deep(.startup-avatar) {
  width: 90px;
  height: 90px;
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
  border: 3px solid #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.template-preview-full :deep(.startup-avatar-svg) {
  width: 100%;
  height: 100%;
}

.template-preview-full :deep(.startup-body) {
  padding: 24px 50px 40px 50px;
}

.template-preview-full :deep(.startup-section) {
  margin-bottom: 20px;
}

.template-preview-full :deep(.startup-section-title) {
  font-size: 15px;
  font-weight: 700;
  color: #0d9488;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
}

.template-preview-full :deep(.startup-divider) {
  height: 1px;
  background: #0d9488;
  margin-bottom: 12px;
  width: 100%;
}

.template-preview-full :deep(.startup-entry) {
  margin-bottom: 12px;
}

.template-preview-full :deep(.startup-entry-header) {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.template-preview-full :deep(.startup-entry-title) {
  font-size: 14px;
  font-weight: 700;
  color: #374151;
}

.template-preview-full :deep(.startup-entry-date) {
  font-size: 13px;
  color: #6b7280;
}

.template-preview-full :deep(.startup-entry-detail) {
  padding-left: 0;
}

.template-preview-full :deep(.startup-detail-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0 0 4px 0;
  line-height: 1.6;
}

.template-preview-full :deep(.startup-detail-label) {
  color: #374151;
  font-weight: 600;
}

.template-preview-full :deep(.startup-detail-text) {
  font-size: 13px;
  color: #4b5563;
  margin: 0 0 4px 0;
  line-height: 1.8;
}

.template-preview-full :deep(.startup-skills) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.template-preview-full :deep(.startup-skill-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.template-preview-full :deep(.startup-skill-label) {
  color: #0d9488;
  font-weight: 600;
}

.template-preview-full :deep(.startup-evaluation) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
  text-align: justify;
}

.template-preview-full :deep(.startup-highlight) {
  color: #dc2626;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .templates-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .library-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .tips-card {
    flex-direction: column;
  }
}
</style>
