/**
 * 许可证状态管理器
 * 
 * 负责获取、显示和更新 VIP 许可证状态
 */

(function(MCPFeedback) {
    'use strict';

    // 确保命名空间存在
    MCPFeedback = MCPFeedback || {};

    /**
     * 许可证状态管理器类
     */
    class LicenseStatusManager {
        constructor() {
            this.licenseInfo = null;
            this.statusData = null;
            this.isLicensed = false;
            this.updateInterval = null;
            this.checkIntervalMs = 60000; // 每分钟检查一次
            
            // DOM 元素引用
            this.elements = {
                container: null,
                statusBadge: null,
                typeText: null,
                daysText: null,
                devicesText: null,
                // 关于页面元素
                aboutStatusBadge: null,
                aboutTypeText: null,
                aboutDaysText: null,
                aboutDevicesText: null,
            };
            
            this.logger = MCPFeedback.logger || console;
        }

        /**
         * 初始化许可证状态管理器
         */
        async init() {
            this.logger.info('[LicenseStatusManager] 初始化许可证状态管理器...');
            
            // 查找或创建 DOM 元素
            this._initDOMElements();
            
            // 获取初始状态
            await this.fetchLicenseStatus();
            
            // 如果未激活，自动跳转到激活页面
            if (!this.isLicensed) {
                this.logger.info('[LicenseStatusManager] 未激活，自动跳转到激活页面...');
                // 使用当前页面跳转，而不是新标签页
                window.location.href = '/api/activation';
                return;
            }
            
            // 启动定时更新
            this._startAutoUpdate();
            
            this.logger.info('[LicenseStatusManager] 初始化完成');
        }

        /**
         * 初始化 DOM 元素
         */
        _initDOMElements() {
            this.elements.container = document.getElementById('licenseStatusContainer');
            this.elements.statusBadge = document.getElementById('licenseStatusBadge');
            this.elements.typeText = document.getElementById('licenseTypeText');
            this.elements.daysText = document.getElementById('licenseDaysText');
            this.elements.devicesText = document.getElementById('licenseDevicesText');
            
            // 关于页面元素
            this.elements.aboutStatusBadge = document.getElementById('aboutLicenseStatusBadge');
            this.elements.aboutTypeText = document.getElementById('aboutLicenseType');
            this.elements.aboutDaysText = document.getElementById('aboutLicenseDays');
            this.elements.aboutDevicesText = document.getElementById('aboutLicenseDevices');
        }

        /**
         * 获取许可证状态
         */
        async fetchLicenseStatus() {
            try {
                const response = await fetch('/api/license-status');
                const data = await response.json();
                
                this.isLicensed = data.is_licensed;
                this.licenseInfo = data.license;
                this.statusData = data.status;
                
                this._updateUI();
                
                this.logger.debug('[LicenseStatusManager] 许可证状态:', data);
                
                return data;
            } catch (error) {
                this.logger.error('[LicenseStatusManager] 获取许可证状态失败:', error);
                this._showError();
                return null;
            }
        }

        /**
         * 更新 UI 显示
         */
        _updateUI() {
            if (!this.elements.container) {
                this._initDOMElements();
            }
            
            if (!this.elements.container) {
                this.logger.warn('[LicenseStatusManager] 未找到许可证状态容器');
                return;
            }
            
            if (this.isLicensed && this.statusData) {
                // 已激活状态
                this.elements.container.classList.remove('not-activated');
                this.elements.container.classList.add('activated');
                
                // 状态徽章
                if (this.elements.statusBadge) {
                    this.elements.statusBadge.textContent = this.statusData.status;
                    this.elements.statusBadge.className = 'license-status-badge activated';
                }
                
                // 授权类型
                if (this.elements.typeText) {
                    this.elements.typeText.textContent = this.statusData.type || '-';
                }
                
                // 剩余天数
                if (this.elements.daysText) {
                    const daysText = this.statusData.expires || '-';
                    this.elements.daysText.textContent = daysText;
                    
                    // 根据剩余天数添加警告样式
                    if (this.licenseInfo && this.licenseInfo.expires_at) {
                        const expiresAt = new Date(this.licenseInfo.expires_at);
                        const now = new Date();
                        const daysRemaining = Math.ceil((expiresAt - now) / (1000 * 60 * 60 * 24));
                        
                        this.elements.daysText.classList.remove('warning', 'critical');
                        if (daysRemaining <= 7) {
                            this.elements.daysText.classList.add('critical');
                        } else if (daysRemaining <= 30) {
                            this.elements.daysText.classList.add('warning');
                        }
                    }
                }
                
                // 设备数
                if (this.elements.devicesText) {
                    this.elements.devicesText.textContent = this.statusData.devices || '-';
                }
                
                // 更新关于页面的信息
                this._updateAboutPage(true);
            } else {
                // 未激活状态
                this.elements.container.classList.remove('activated');
                this.elements.container.classList.add('not-activated');
                
                if (this.elements.statusBadge) {
                    this.elements.statusBadge.textContent = '未激活';
                    this.elements.statusBadge.className = 'license-status-badge not-activated';
                }
                
                if (this.elements.typeText) {
                    this.elements.typeText.textContent = '-';
                }
                
                if (this.elements.daysText) {
                    this.elements.daysText.textContent = '-';
                    this.elements.daysText.classList.remove('warning', 'critical');
                }
                
                if (this.elements.devicesText) {
                    this.elements.devicesText.textContent = '-';
                }
                
                // 更新关于页面的信息
                this._updateAboutPage(false);
            }
        }

        /**
         * 更新关于页面的授权信息
         */
        _updateAboutPage(isActivated) {
            if (isActivated && this.statusData) {
                if (this.elements.aboutStatusBadge) {
                    this.elements.aboutStatusBadge.textContent = this.statusData.status;
                    this.elements.aboutStatusBadge.className = 'license-status-badge activated';
                }
                
                if (this.elements.aboutTypeText) {
                    this.elements.aboutTypeText.textContent = this.statusData.type || '-';
                }
                
                if (this.elements.aboutDaysText) {
                    this.elements.aboutDaysText.textContent = this.statusData.expires || '-';
                    
                    // 根据剩余天数设置颜色
                    const daysRemaining = this.getDaysRemaining();
                    if (daysRemaining <= 7) {
                        this.elements.aboutDaysText.style.color = '#ff6b6b';
                    } else if (daysRemaining <= 30) {
                        this.elements.aboutDaysText.style.color = '#ffa500';
                    } else {
                        this.elements.aboutDaysText.style.color = '#00ff88';
                    }
                }
                
                if (this.elements.aboutDevicesText) {
                    this.elements.aboutDevicesText.textContent = this.statusData.devices || '-';
                }
            } else {
                if (this.elements.aboutStatusBadge) {
                    this.elements.aboutStatusBadge.textContent = '未激活';
                    this.elements.aboutStatusBadge.className = 'license-status-badge not-activated';
                }
                
                if (this.elements.aboutTypeText) {
                    this.elements.aboutTypeText.textContent = '-';
                }
                
                if (this.elements.aboutDaysText) {
                    this.elements.aboutDaysText.textContent = '-';
                    this.elements.aboutDaysText.style.color = 'var(--text-primary)';
                }
                
                if (this.elements.aboutDevicesText) {
                    this.elements.aboutDevicesText.textContent = '-';
                }
            }
        }

        /**
         * 显示错误状态
         */
        _showError() {
            if (!this.elements.container) {
                this._initDOMElements();
            }
            
            if (this.elements.statusBadge) {
                this.elements.statusBadge.textContent = '状态未知';
                this.elements.statusBadge.className = 'license-status-badge error';
            }
        }

        /**
         * 启动自动更新
         */
        _startAutoUpdate() {
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
            }
            
            this.updateInterval = setInterval(() => {
                this.fetchLicenseStatus();
            }, this.checkIntervalMs);
        }

        /**
         * 停止自动更新
         */
        stopAutoUpdate() {
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
                this.updateInterval = null;
            }
        }

        /**
         * 跳转到激活页面
         */
        goToActivation() {
            try {
                // 使用当前窗口跳转，避免浏览器阻止弹出窗口
                window.location.href = '/api/activation';
            } catch (error) {
                this.logger.error('[LicenseStatusManager] 跳转到激活页面失败:', error);
                // 如果跳转失败，尝试使用 window.open 作为后备
                const newWindow = window.open('/api/activation', '_blank');
                if (!newWindow) {
                    alert('无法打开激活页面，请手动访问: ' + window.location.origin + '/api/activation');
                }
            }
        }

        /**
         * 获取当前许可证信息
         */
        getLicenseInfo() {
            return {
                isLicensed: this.isLicensed,
                license: this.licenseInfo,
                status: this.statusData,
            };
        }

        /**
         * 计算剩余天数
         */
        getDaysRemaining() {
            if (!this.licenseInfo || !this.licenseInfo.expires_at) {
                return 0;
            }
            
            const expiresAt = new Date(this.licenseInfo.expires_at);
            const now = new Date();
            const daysRemaining = Math.ceil((expiresAt - now) / (1000 * 60 * 60 * 24));
            
            return Math.max(0, daysRemaining);
        }

        /**
         * 销毁实例
         */
        destroy() {
            this.stopAutoUpdate();
            this.elements = {
                container: null,
                statusBadge: null,
                typeText: null,
                daysText: null,
                devicesText: null,
                aboutStatusBadge: null,
                aboutTypeText: null,
                aboutDaysText: null,
                aboutDevicesText: null,
            };
        }
    }

    // 注册到全局命名空间
    MCPFeedback.LicenseStatusManager = LicenseStatusManager;

    // 创建全局实例
    MCPFeedback.licenseStatusManager = null;

    // 初始化函数
    MCPFeedback.initLicenseStatus = async function() {
        if (!MCPFeedback.licenseStatusManager) {
            MCPFeedback.licenseStatusManager = new LicenseStatusManager();
            await MCPFeedback.licenseStatusManager.init();
        }
        return MCPFeedback.licenseStatusManager;
    };

})(window.MCPFeedback = window.MCPFeedback || {});
