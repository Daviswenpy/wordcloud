#/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append("/opt/skyguard/www/app")
import utils

lang = "zh_CN"

messages = {
        0x01: {
            "zh_CN" : "用户名:",
            "en" : "User name:"
            },
        0x02: {
            "zh_CN" : "密码:",
            "en" : "Password:"
            },
        0x03: {
            "zh_CN" : "确认密码:",
            "en" : "Confirm Password:"
            },
        0x04: {
            "zh_CN" : "用户名无效。请重新输入。",
            "en" : "Invalid user name. Please re-enter."
            },
        0x05: {
            "zh_CN" : "将以下编码提供给SkyGuard技术支持获取密钥，方可重设密码",
            "en" : "Send following token to SkyGuard TS to obtain a TS password."
            },
        0x06: {
            "zh_CN" : "编码:", # 6-digit passcode for skyguard Technical Support user. It needs to be translated to 8-digit password before use.
            "en" : "Token:"
            },
        0x07: {
            "zh_CN" : "密钥:", # 8-digit password from skyguard TS
            "en" : "TS Password:"
            },
        0x08: {
            "zh_CN" : "请输入新的%s密码", # replace %s with username
            "en" : "Enter a new password for %s"
            },
        0x09: {
            "zh_CN" : "两次密码输入不同，请重新输入。",
            "en" : "You entered a different password. Please re-check and enter again."
            },
        0x0a: {
            "zh_CN" : "密码重置成功。",
            "en" : "Password reset successfully."
            },
        0x0b: {
            "zh_CN" : "描述:",
            "en" : "Description:"
            },
        0x0c: {
            "zh_CN" : "%s设备密码已经重置完成。按任意键返回登录界面并使用新密码登录。", # replace %s with username
            "en" : "Password reset completed on appliance %s. Press any button to return to Logon page and log on with the new password."
            },
        0x0d: {
            "zh_CN" : "密码重置成功。",
            "en" : "Password reset successfully."
            },
        0x0e: {
            "zh_CN" : "按回车键返回主菜单。",
            "en" : "Press \"Enter\" to return to Main Menu."
            },
        0x0f: {
            "zh_CN" : "密码错误。",
            "en" : "Incorrect password."
            },
        0x10: {
            "zh_CN" : "初始化",
            "en" : "Initialization",
            },
        0x11: {
            "zh_CN" : "命令控制台", # command line console
            "en" : "Command Line Console"
            },
        0x12: {
            "zh_CN" : "退出",
            "en" : "Quit"
            },
        0x13: {
            "zh_CN" : "输入选项:",
            "en" : "Input your option:"
            },
        0x14: {
            "zh_CN" : "请确认是否同意所有许可协议内容？Y/N(No):", # EULA agreement
            "en" : "Do you accept all the terms of the License Agreement? Y/N(No):"
            },
        0x15: {
            "zh_CN" : "初始化失败。请重试。如问题仍未解决，请联系天空卫士技术支持。", 
            "en" : "Failed to initialize your appliance. Please retry. If the issue persists, contact SkyGuard TS for assistance."
            },
        0x16: {
            "zh_CN" : "%s设备初始化完成，配置的IP地址为: %s。", # replace the first %s with device type, replace the second %s with ip address
            "en" : "Initialization completed on appliance %s. IP address configured as: %s."
            },
        0x17: {
            "zh_CN" : "初始化成功。",
            "en" : "Initialization completed."
            },
        0x18: {
            "zh_CN" : "数据库初始化失败。", 
            "en" : "Failed to initialize database."
            },
        0x19: {
            "zh_CN" : "DLP服务无法启动，请重试。如问题仍未解决，请联系天空卫士技术支持。", 
            "en" : "Failed to start DLP service. Please retry. If the issue persists, contact SkyGuard TS for assistance."
            },
        0x1a: {
            "zh_CN" : "请仔细阅读许可协议。",
            "en" : "Please read the License Agreement carefully."
            },
        0x1b: {
            "zh_CN" : "第%d步，共%d步",
            "en" : "Step %d, %d steps in total."
            },
        0x1c: {
            "zh_CN" : "任何菜单下按(Ctrl+C)键均可退回到主菜单。",
            "en" : "Press \"Ctrl+C\" to return to main menu no matter which menu you are on." 
            },
        0x1d: {
            "zh_CN" : "IP地址",
            "en" : "IP Address"
            },
        0x1e: {
            "zh_CN" : "掩码",
            "en" : "Netmask"
            },
        0x1f: {
            "zh_CN" : "网关",
            "en" : "Gateway"
            },
        0x20: {
            "zh_CN" : "DNS服务器",
            "en" : "DNS Servers"
            },
        0x21: {
            "zh_CN" : "请确认您的网络配置信息:",
            "en" : "Confirm your network configuration:"
            },
        0x22: {
            "zh_CN" : "管理网卡:",
            "en" : "Network management:"
            },
        0x23: {
            "zh_CN" : "请确认是否保存网络配置信息？Y/N(No):",
            "en" : "Are you sure you want to save the network settings? Y/N (No):" 
            },
        0x24: {
            "zh_CN" : "修改主机名称",
            "en" : "Reset hostname" 
            },
        0x25: {
            "zh_CN" : "主机名称",
            "en" : "Hostname"
            },
        0x26: {
            "zh_CN" : "您输入的主机名称为：",
            "en" : "The hostname you entered is: "
            },
        0x27: {
            "zh_CN" : "请确认是否保存新的主机名称？Y/N(No):",
            "en" : "Are you sure you want to save the new hostname? Y/N (No):"
            },
        0x28: {
            "zh_CN" : "当前日期：",
            "en" : "Current Date: "
            },
        0x29: {
            "zh_CN" : "请输入新的日期，格式(yyyy-mm-dd)：", 
            "en" : "Enter new date (yyyy-mm-dd): "
            },
        0x2a: {
            "zh_CN" : "当前时间：",
            "en" : "Current Time: "
            },
        0x2b: {
            "zh_CN" : "请输入新的时间，格式(hh:mm:ss)：",
            "en" : "Enter new time (hh:mm:ss): "
            },
        0x2c: {
            "zh_CN" : "请确认是否保存新的日期时间？Y/N(No):",
            "en" : "Are you sure you want to save the new date and time? Y/N (No)"
            },
        0x2d: {
            "zh_CN" : "您必须重新设置设备管理员密码。",
            "en" : "You must reset password for Admin account."
            },
        0x2e: {
            "zh_CN" : "两次密码输入不同。请重新输入。",
            "en" : "You entered a different password. Please check and re-enter."
            },
        0x2f: {
            "zh_CN" : "请确认是否保存新的密码？Y/N(No):",
            "en" : "Are you sure you want to save the new password? Y/N (No)" 
            },
        0x30: {
            "zh_CN" : "初始化信息确认：",
            "en" : "Confirm your initialization settings."
            },
        0x31: {
            "zh_CN" : "网络配置：",
            "en" : "Network settings:"
            },
        0x32: {
            "zh_CN" : "网卡名称：",
            "en" : "Network adapter:"
            },
        0x33: {
            "zh_CN" : "网卡IP地址：",
            "en" : "IP address:"
            },
        0x34: {
            "zh_CN" : "网卡掩码：", 
            "en" : "Subnet mask:"
            },
        0x35: {
            "zh_CN" : "默认网关：",
            "en" : "Default gateway:"
            },
        0x36: {
            "zh_CN" : "日期时间:",
            "en" : "Date and time:"
            },
        0x37: {
            "zh_CN" : "管理员密码：",
            "en" : "Admin password:"
            },
        0x38: {
            "zh_CN" : "数据库位置: ",
            "en" : "Database location: "
            },
        0x39: {
            "zh_CN" : "本地数据库",
            "en" : "Local database"
            },
        0x3a: {
            "zh_CN" : "远程数据库",
            "en" : "Remote database"           
            },
        0x3b: {
            "zh_CN" : "PostgreSQL数据库:",
            "en" : "PostgreSQL Database"
            },
        0x3c: {
            "zh_CN" : "数据库主机名/IP地址:",
            "en" : "Database host name/IP address:"
            },
        0x3d: {
            "zh_CN" : "端口:",
            "en" : "Port:"
            },
        0x3e: {
            "zh_CN" : "数据库用户名:",
            "en" : "Database user name:"
            },
        0x3f: {
            "zh_CN" : "数据库密码:",
            "en" : "Database password:"
            },
        0x40: {
            "zh_CN" : "Elasticsearch数据库:",
            "en" : "Elasticsearch Database"
            },
        0x41: {
            "zh_CN" : "请确认是否保存数据库配置？Y/N(No):",
            "en" : "Are you sure you want to save database settings? Y/N (No):"
            },
        0x42: {
            "zh_CN" : "请选择数据库位置:", 
            "en" : "Choose database location:"
            },
        0x43: {
            "zh_CN" : "请选择(%s):",
            "en" : "Please choose (%s):"
            },
        0x44: {
            "zh_CN" : "保存配置中...", 
            "en" : "Saving configuration..."
            },
        0x45: {
            "zh_CN" : "%s设备初始化失败，重试一次。", # replace %s with device type 
            "en" : "Failed to initialize appliance %s."
            },
        0x46: {
            "zh_CN" : "请确认是否立即注册到管理平台？Y/N(No):",
            "en" : "Are you sure you want to register to management console now? Y/N (No)" 
            },
        0x47: {
            "zh_CN" : "请输入管理平台的IP地址：",
            "en" : "Management console IP address: "
            },
        0x48: {
            "zh_CN" : "请确认是否立即注册？Y/N(No):",
            "en" : "Are you sure you want to register now? Y/N (No)"
            },
        0x49: {
            "zh_CN" : "设备成功注册至管理平台(%s)。",
            "en" : "Registered to management console (%s) successfully. "
            },
        0x4a: {
            "zh_CN" : "您可以通过WebUI的方式对设备进行进一步管理。请在浏览器上输入下面的URL打开管理平台管理界面对这台设备进行管理：",
            "en" : "You can manage all the other configurations of an appliance via management console. Type the following URL in your browser to connect to console. "
            },
        0x4b: {
            "zh_CN" : "注册成功。",
            "en" : "Registered successfully."
            },
        0x4c: {
            "zh_CN" : "设备注册到管理平台(%s)失败。", 
            "en" : "Failed to register appliance on console (%s)."
            },
        0x4d: {
            "zh_CN" : "注册失败。",
            "en" : "Failed to register."
            },
        0x4e: {
            "zh_CN" : "按回车键返回主菜单。",
            "en" : "Press \"Enter\" to return to main menu."
            },
        0x4f: {
            "zh_CN" : "开始收集日志",
            "en" : "Start collecting logs"
            },
        0x50: {
            "zh_CN" : "列出已收集的日志",
            "en" : "List collected logs"
            },
        0x51: {
            "zh_CN" : "上传日志",
            "en" : "Upload logs"
            },
        0x52: {
            "zh_CN" : "删除日志",
            "en" : "Remove logs"
            },
        0x53: {
            "zh_CN" : "获取日志列表失败。", 
            "en" : "Failed to obtain log list."
            },
        0x54: {
            "zh_CN" : "序号",
            "en" : "ID"
            },
        0x55: {
            "zh_CN" : "名字",
            "en" : "Name"
            },
        0x56: {
            "zh_CN" : "大小",
            "en" : "Size"
            },
        0x57: {
            "zh_CN" : "空间不足，无法收集。",
            "en" : "Failed to collect logs. "
            },
        0x58: {
            "zh_CN" : "正在收集日志......",
            "en" : "Collecting logs..."
            },
        0x59: {
            "zh_CN" : "收集日志失败。", 
            "en" : "Failed  to collect logs."
            },
        0x5a: {
            "zh_CN" : "收集完成:",
            "en" : "Log collection completed:"
            },
        0x5b: {
            "zh_CN" : "获取日志失败。",  
            "en" : "Failed to obtain logs."
            },
        0x5c: {
            "zh_CN" : "请输入要上传的日志序号:", 
            "en" : "Enter the ID of the log you want to upload:"
            },
        0x5d: {
            "zh_CN" : "未找到该日志。请输入正确的日志序号",
            "en" : "Log ID not found. Please re-check and enter a correct log ID."
            },
        0x5e: {
            "zh_CN" : "请输入上传日志的FTP地址:",
            "en" : "Enter FTP address to upload logs"
            },
        0x5f: {
            "zh_CN" : "用户名:",
            "en" : "User name:"
            },
        0x60: {
            "zh_CN" : "密码:",
            "en" : "Password:"
            },
        0x61: {
            "zh_CN" : "正在上传......",
            "en" : "Uploading..."
            },
        0x62: {
            "zh_CN" : "上传成功。",
            "en" : "Uploaded Successfully."
            },
        0x63: {
            "zh_CN" : "FTP用户名或者密码错误",
            "en" : "Incorrect FTP user name or password."
            },
        0x64: {
            "zh_CN" : "未找到该文件。",
            "en" : "File not found."
            },
        0x65: {
            "zh_CN" : "请输入要删除的日志序号:", 
            "en" : "Enter ID of the log you want to remove:"
            },
        0x66: {
            "zh_CN" : "正在删除......",
            "en" : "Removing..."
            },
        0x67: {
            "zh_CN" : "删除日志失败。", 
            "en" : "Failed to remove log."
            },
        0x68: {
            "zh_CN" : "删除成功。",
            "en" : "Removed successfully."
            },
        0x69: {
            "zh_CN" : "不能指定loopback网卡的MTU", 
            "en" : "Unable to configure MTU for loopback adapter. " 
            },
        0x6a: {
            "zh_CN" : "请设置MTU值，仅可设为整数", 
            "en" : "Set MTU value, only integers are allowed."
            },
        0x6b: {
            "zh_CN" : "指定的网卡不存在。",
            "en" : "Network adapter is not found."
            },
        0x6c : {
            "zh_CN" : "设置网卡MTU失败。", 
            "en" : "Failed to configure MTU adapter."
            },
        0x6d: {
            "zh_CN" : "未找到任何时区信息",
            "en" : "Time zone information is not found."
            },
        0x6e: {
            "zh_CN" : "更新成功。", 
            "en" : "Updated successfully."
            },
        0x6f: {
            "zh_CN" : "操作成功。", # reboot, start/stop service
            "en" : "Executed successfully."
            },
        0x70: {
            "zh_CN" : "本机license不合法，license:", 
            "en" : "Invalid license. License:"
            },
        0x71: {
            "zh_CN" : "本机并未指定license",
            "en" : "License is not configured."
            },
        0x72: {
            "zh_CN" : "天空卫士",
            "en" : "SkyGuard"
            },
        0x73: {
            "zh_CN" : "启动时间",
            "en" : "Start time"
            },
        0x74: {
            "zh_CN" : "当前时间",
            "en" : "Current time"
            },
        0x75: {
            "zh_CN" : "型号",
            "en" : "Model"
            },
        0x76: {
            "zh_CN" : "授权功能:",
            "en" : "Authorized function:"
            },
        0x77: {
            "zh_CN" : "CPU使用率:",
            "en" : "CPU usage:"
            },
        0x78: {
            "zh_CN" : "内存使用率:",
            "en" : "Memory usage:"
            },
        0x79: {
            "zh_CN" : "系统磁盘使用率:",
            "en" : "System drive usage:"
            },
        0x7a: {
            "zh_CN" : "数据磁盘使用率:",
            "en" : "Data drive usage:"
            },
        0x7b: {
            "zh_CN" : "目标网络",
            "en" : "Target network"
            },
        0x7c: {
            "zh_CN" : "网卡",
            "en" : "Network adapter"
            },
        0x7d: {
            "zh_CN" : "类型",
            "en" : "Type"
            },
        0x7e: {
            "zh_CN" : "静态路由",
            "en" : "Static routing"
            },
        0x7f: {
            "zh_CN" : "策略路由",
            "en" : "Policy based routing"
            },
        0x80: {
            "zh_CN" : "MAC地址",
            "en" : "MAD address"
            },
        0x81: {
            "zh_CN" : "状态",
            "en" : "Status"
            },
        0x82: {
            "zh_CN" : "模式",
            "en" : "Mode"
            },
        0x83: {
            "zh_CN" : "速度",
            "en" : "Speed"
            },
        0x84: {
            "zh_CN" : "双工模式",
            "en" : "Duplex mode"
            },
        0x85: {
            "zh_CN" : "已连接",
            "en" : "Connected"
            },
        0x86: {
            "zh_CN" : "未连接",
            "en" : "Disconnected"
            },
        0x87: {
            "zh_CN" : "监控",
            "en" : "Monitor"
            },
        0x88: {
            "zh_CN" : "桥接",
            "en" : "Bridge"
            },
        0x89: {
            "zh_CN" : "网络",
            "en" : "Network"
            },
        0x8a: {
            "zh_CN" : "未找到您要删除的路由",
            "en" : "The router to remove is not found."
            },
        0x8b: {
            "zh_CN" : "启用技术支持帐户成功。请输入六位登录码:",
            "en" : "TS account enabled. Enter the 6-digit password:"
            },
        0x8c: {
            "zh_CN" : "禁用技术支持帐户成功",
            "en" : "TS account disabled."
            },
        0x8d: {
            "zh_CN" : "该命令不在支持列表中:",
            "en" : "No such command in commands list:"
            },
        0x8e: {
            "zh_CN" : "SkyGuard UCSS统一内容安全管理平台控制台命令列表",
            "en" : "SkyGuard UCSS commands"
            },
        0x8f: {
            "zh_CN" : "SkyGuard UCSG统一内容安全网关控制台命令列表",
            "en" : "SkyGuard UCSG commands"
            },
        0x90: {
            "zh_CN" : "SkyGuard UCSS Lite统一内容安全扩展服务器控制台命令列表",
            "en" : "SkyGuard UCSS Lite commands"
            },
        0x91: {
            "zh_CN" : "SkyGuard WebService Inspector控制台命令列表",
            "en" : "SkyGuard WebService Inspector commands"
            },
        0x92: {
            "zh_CN" : "SkyGuard SWG统一内容安全网关控制台命令列表",
            "en" : "SkyGuard SWG commands"
            },
        0x93: {
            "zh_CN" : "SkyGuard MAG统一内容安全网关控制台命令列表",
            "en" : "SkyGuard MAG commands"
            },
        0x94: {
            "zh_CN" : "使用help <command>查看使用帮助。",
            "en" : "Use help command to access help information."
            },
        0x95: {
            "zh_CN" : "激活OCR",
            "en" : "Activate OCR"
            },
        0x96: {
            "zh_CN" : "备份当前设备配置",
            "en" : "Backup current settings"
            },
        0x97: {
            "zh_CN" : "开启/关闭/清除coredump",
            "en" : "Enable/Disable/Clear coredump"
            },
        0x98: {
            "zh_CN" : "更新日期",
            "en" : "Last updated"
            },
        0x99: {
            "zh_CN" : "关闭网卡绑定",
            "en" : "Disable bonding network adapters"
            },
        0x9a: {
            "zh_CN" : "运行初始化脚本",
            "en" : "Run initialization scripts"
            },
        0x9b: {
            "zh_CN" : "查看历史命令",
            "en" : "View command history"
            },
        0x9c: {
            "zh_CN" : "更新主机名称",
            "en" : "Update host name"
            },
        0x9d: {
            "zh_CN" : "更新网卡的MTU",
            "en" : "Update NIC MTU"
            },
        0x9e: {
            "zh_CN" : "执行系统%s命令", # replace %s with system command
            "en" : "Execute %s command"
            },
        0x9f: {
            "zh_CN" : "退出命令行控制界面",
            "en" : "Quit CLI"
            },
        0x100: {
            "zh_CN" : "重启主机",
            "en" : "Restart"
            },
        0x101: {
            "zh_CN" : "注册当前设备至UCSS (注:UCSS设备无法使用此命令)",
            "en" : "Register appliance to UCSS. The command is disabled on UCSS appliance."
            },
        0x102: {
            "zh_CN" : "从备份列表中恢复设备配置",
            "en" : "Recover settings from backup list"
            },
        0x103: {
            "zh_CN" : "添加|删除策略路由",
            "en" : "Add|Remove policy based router"
            },
        0x104: {
            "zh_CN" : "添加|删除静态路由",
            "en" : "Add|Remove static router"
            },
        0x105: {
            "zh_CN" : "查看/启动/停止DLP服务",
            "en" : "View/Enable/Disable DLP service"
            },
        0x106: {
            "zh_CN" : "显示CPU使用率",
            "en" : "Show CPU usage"
            },
        0x107: {
            "zh_CN" : "显示当前日期",
            "en" : "Show current date"
            },
        0x108: {
            "zh_CN" : "显示设备ID",
            "en" : "Show appliance ID"
            },
        0x109: {
            "zh_CN" : "显示硬盘使用率",
            "en" : "Show drive usage"
            },
        0x10a: {
            "zh_CN" : "显示DNS",
            "en" : "Show DNS"
            },
        0x10b: {
            "zh_CN" : "显示网关",
            "en" : "Show gateway"
            },
        0x10c: {
            "zh_CN" : "显示主机名",
            "en" : "Show hostname"
            },
        0x10d: {
            "zh_CN" : "显示IP, 网关等信息", 
            "en" : "Show network information including IP address, gateway and so on"
            },
        0x10e: {
            "zh_CN" : "显示内存使用率",
            "en" : "Show memory usage"
            },
        0x10f: {
            "zh_CN" : "显示设备型号",
            "en" : "Show appliance model"
            },
        0x110: {
            "zh_CN" : "显示网卡的MTU",
            "en" : "Show NIC MTU"
            },
        0x111: {
            "zh_CN" : "显示路由信息",
            "en" : "Show router information"
            },
        0x112: {
            "zh_CN" : "显示当前时间",
            "en" : "Show current time"
            },
        0x113: {
            "zh_CN" : "显示当前时区",
            "en" : "Show current time zone"
            },
        0x114: {
            "zh_CN" : "显示系统版本",
            "en" : "Show system version"
            },
        0x115: {
            "zh_CN" : "关闭主机",
            "en" : "shut down the appliance"
            },
        0x116: {
            "zh_CN" : "启用|禁用技术支持帐户",
            "en" : "Enable/Disable TS account"
            },
        0x117: {
            "zh_CN" : "更新时间",
            "en" : "Update time"
            },
        0x118: {
            "zh_CN" : "删除所有授信地址",
            "en" : "Clear all trusted URLs"
            },
        0x119: {
            "zh_CN" : "清除缓存",
            "en" : "Clear cache"
            },
        0x11a: {
            "zh_CN" : "收集日志",
            "en" : "Collect logs"
            },
        0x11b: {
            "zh_CN" : "立即同步时间",
            "en" : "Synchronize time now"
            },
        0x11c: {
            "zh_CN" : "全局例外",
            "en" : "Global exception"
            },
        0x11d: {
            "zh_CN" : "欢迎使用天空卫士DLP产品命令行控制界面",
            "en" : "Welcome to SkyGuard DLP Command Line Interface"
            },
        0x11e: {
            "zh_CN" : "退出命令行控制界面",
            "en" : "Quit CLI"
            },
        0x120: {
            "zh_CN" : "仅UCSS设备支持手动更新日志。", 
            "en" : "Manual date update is only supported on UCSS appliance"
            },
        0x121: {
            "zh_CN" : "输入参数数目不合法, 请参考帮助文档。",
            "en" : "Parameters you entered is invalid. See Help for more information."
            },
        0x122: {
            "zh_CN" : "输入日期格式不合法。格式应为yyyy-mm-dd。",
            "en" : "Incorrect date format. Re-enter date in form of yyyy-mm-dd "
            },
        0x123: {
            "zh_CN" : "更新日期失败, 请联系技术支持人员。", 
            "en" : "Failed to update date information. Contact SkyGuard TS for assistance." 
            },
        0x124: {
            "zh_CN" : "执行命令失败, 请联系技术支持人员。错误内容:",
            "en" : "Failed to execute command. Contact SkyGuard TS for assistance. Error details:"
            },
        0x125: {
            "zh_CN" : "此设备不支持更新时间。",
            "en" : "Time update is not supported on the appliance."
            },
        0x126: {
            "zh_CN" : "输入时间格式不合法, 格式应为hh:mm:ss。", 
            "en" : "Incorrect time format. Re-enter time in form of hh:mm:ss."
            },
        0x127: {
            "zh_CN" : "更新时间失败, 请联系技术支持人员。",
            "en" : "Failed to update time information. Contact SkyGuard TS for assistance."
            },
        0x128: {
            "zh_CN" : "更新主机名称失败, 请联系技术支持人员。",
            "en" : "Failed to update host name. Contact SkyGuard TS for assistance."
            },
        0x129: {
            "zh_CN" : "请确认是否重启？Y/N(No):",
            "en" : "Are you sure you want to restart? Y/N (No)"
            },
        0x12a: {
            "zh_CN" : "重启失败, 请联系技术支持人员",
            "en" : "Failed to restart. Contact SkyGuard TS for assistance."
            },
        0x12b: {
            "zh_CN" : "请确认是否关机？Y/N(No):",
            "en" : "Are you sure you want to shut down? Y/N (No)"
            },
        0x12c: {
            "zh_CN" : "关机失败, 请联系技术支持人员",
            "en" : "Failed to shut down. Contact SkyGuard TS for assistance."
            },
        0x12d: {
            "zh_CN" : "获取设备信息失败, 请联系技术支持人员", 
            "en" : "Failed to obtain appliance information. Contact SkyGuard TS for assistance."
            },
        0x12e: {
            "zh_CN" : "此设备不支持添加和删除路由",
            "en" : "Adding and removing a router is not supported on the appliance."
            },
        0x130: {
            "zh_CN" : "输入的网卡参数不合法。应为mgmt/mta/br0/p1/p2中的一项。",
            "en" : "NIC parameter you entered is invalid. Re-enter one of the following: mgmt/mta/br0/p1/p2."
            },
        0x131: {
            "zh_CN" : "添加静态路由失败, 请联系技术支持人员",
            "en" : "Failed to add static router. Contact SkyGuard TS for assistance."
            },
        0x132: {
            "zh_CN" : "删除静态路由失败, 请联系技术支持人员",
            "en" : "Failed to remove static router. Contact SkyGuard TS for assistance."
            },
        0x133: {
            "zh_CN" : "添加策略路由失败, 请联系技术支持人员",
            "en" : "Failed to add policy based router. Contact SkyGuard TS for assistance."
            },
        0x134: {
            "zh_CN" : "删除策略路由失败, 请联系技术支持人员",
            "en" : "Failed to remove policy based router. Contact SkyGuard TS for assistance."
            },
        0x135: {
            "zh_CN" : "添加静态路由",
            "en" : "Add static router"
            },
        0x136: {
            "zh_CN" : "删除静态路由",
            "en" : "Remove static router"
            },
        0x137: {
            "zh_CN" : "添加策略路由",
            "en" : "Add policy based router"
            },
        0x138: {
            "zh_CN" : "删除策略路由",
            "en" : "Remove policy based router"
            },
        0x139: {
            "zh_CN" : "启用或禁用技术支持帐户失败。请联系技术支持人员。",
            "en" : "Failed to enable or disable SkyGuard TS account. Contact SkyGuard TS for assistance. "
            },
        0x13a: {
            "zh_CN" : "启用|禁用技术支持帐户",
            "en" : "Enable|Disable SkyGuard TS account"
            },
        0x13b: {
            "zh_CN" : "技术支持帐户的登录名称为skyguardts。启用后会返回6位登录码。",
            "en" : "SkyGuard TS account user name is skyguardts. The system returns a 6-digit password after the account is enabled."
            },
        0x13c: {
            "zh_CN" : "清除所有授信IP地址成功。", 
            "en" : "All trusted IP address are cleared successfully."
            },
        0x13d: {
            "zh_CN" : "清除所有授信地址失败。",
            "en" : "Failed to clear all trusted IP addresses."
            },
        0x13e: {
            "zh_CN" : "清除所有的授信IP地址。", 
            "en" : "Remove all trusted IP addresses. "
            },
        0x140: {
            "zh_CN" : "此设备类型不支持此操作。",
            "en" : "Operation is not supported on the appliance."
            },
        0x141: {
            "zh_CN" : "此操作需要重启服务，是否继续？Y/N(No):",
            "en" : "Restart is needed to complete the operation, do you want to continue? Y/N (No)"
            },
        0x142: {
            "zh_CN" : "清除成功",
            "en" : "Cleared successfully"
            },
        0x143: {
            "zh_CN" : "日志的收集，查看，上传，删除",
            "en" : "The collecting, viewing, uploading and removal of logs."
            },
        0x144: {
            "zh_CN" : "同步时间成功。",
            "en" : "Time synchronized successfully."
            },
        0x145: {
            "zh_CN" : "同步时间失败。",
            "en" : "Failed to synchronize time."
            },
        0x146: {
            "zh_CN" : "立即同步时间",
            "en" : "Synchronize time now"
            },
        0x147: {
            "zh_CN" : "输入IP地址不合法。请重新输入。",
            "en" : "The IP address you entered is not valid. Please check and re-enter. "
            },
        0x148: {
            "zh_CN" : "激活成功。",
            "en" : "Activated successfully."
            },
        0x149: {
            "zh_CN" : "激活失败。",
            "en" : "Failed to activate."
            },
        0x14a: {
            "zh_CN" : "无法连接网络。",
            "en" : "Failed to connect to network."
            },
        0x14b: {
            "zh_CN" : "错误的命令。",
            "en" : "Incorrect command."
            },
        0x14c: {
            "zh_CN" : "UCSS管理",
            "en" : "UCSS management"
            },
        0x14d: {
            "zh_CN" : "安全引擎",
            "en" : "CAE"
            },
        0x14e: {
            "zh_CN" : "指纹管理",
            "en" : "FPDB"
            },
        0x150: {
            "zh_CN" : "数据提取",
            "en" : "DSA"
            },
        0x151: {
            "zh_CN" : "ICAP代理",
            "en" : "ICAP"
            },
        0x152: {
            "zh_CN" : "图像识别",
            "en" : "OCR"
            },
        0x153: {
            "zh_CN" : "设备管理",
            "en" : "DM"
            },
        0x154: {
            "zh_CN" : "协议分析",
            "en" : "ATS"
            },
        0x155: {
            "zh_CN" : "邮件转发",
            "en" : "MTA"
            },
        0x156: {
            "zh_CN" : "透明用户标示服务", #Q PM没有定义这个术语。Websense文档里面叫做Transparent identification
            "en" : "Transparent identification"
            },
        0x157: {
            "zh_CN" : "系统错误",
            "en" : "system error"
            },
        0x158: {
            "zh_CN" : "服务名称",
            "en" : "Service name"
            },
        0x159: {
            "zh_CN" : "服务状态",
            "en" : "Service status"
            },
        0x15a: {
            "zh_CN" : "操作",
            "en" : "Operation"
            },
        0x15b: {
            "zh_CN" : "停止",
            "en" : "Stop"
            },
        0x15c: {
            "zh_CN" : "运行", 
            "en" : "Execute"
            },
        0x15d: {
            "zh_CN" : "按Ctrl+C退出",
            "en" : "Press Ctrl+C to quit"
            },
        0x15e: {
            "zh_CN" : "请选择操作(A-I, R键刷新),可使用逗号分隔:",
            "en" : "Choose operations (A-I, press R to Refresh). Separate your choices with a comma:"
            },
        0x160: {
            "zh_CN" : "请选择网卡：",
            "en" : "Select network adapter:"
            },
        0x161: {
            "zh_CN" : "管理网卡",
            "en" : "Manage network adapter"
            },
        0x162: {
            "zh_CN" : "此型号不支持网卡绑定功能",
            "en" : "The appliance model does not support bonding network adapters."
            },
        0x163: {
            "zh_CN" : "MTA网卡",
            "en" : "MTA adapter"
            },
        0x164: {
            "zh_CN" : "Bypass网卡",
            "en" : "Bypass adapter"
            },
        0x165: {
            "zh_CN" : "配置",
            "en" : "Configuration"
            },
        0x166: {
            "zh_CN" : "事件",
            "en" : "Event"
            },
        0x167: {
            "zh_CN" : "证据文件", 
            "en" : "Forensics"
            },
        0x168: {
            "zh_CN" : "网络",
            "en" : "Network"
            },
        0x169: {
            "zh_CN" : "选择备份内容:", 
            "en" : "Choose the content to backup:"
            },
        0x16a: {
            "zh_CN" : "备份成功",
            "en" : "Backup completed successfully."
            },
        0x16b: {
            "zh_CN" : "备份失败",
            "en" : "Failed to backup."
            },
        0x16c: {
            "zh_CN" : "备份名称",
            "en" : "Appliance name:"
            },
        0x16d: {
            "zh_CN" : "备份时间",
            "en" : "Backup time"
            },
        0x16e: {
            "zh_CN" : "备份版本",
            "en" : "Backup version"
            },
        0x170: {
            "zh_CN" : "备份内容",
            "en" : "Backup contents"
            },
        0x171: {
            "zh_CN" : "请选择要恢复的文件序号:", 
            "en" : "Enter ID of the file you want to recover:"
            },
        0x172: {
            "zh_CN" : "请确认是否恢复？Y/N(No):",  
            "en" : "Are you sure you want to recover? Y/N (No)"
            },
        0x173: {
            "zh_CN" : "恢复备份失败,请联系天空卫士技术支持。", 
            "en" : "Failed to recover from backup. Contact SkyGuard TS for support."
            },
        0x174: {
            "zh_CN" : "无可用备份文件。",
            "en" : "No backup file available."
            },
        0x175: {
            "zh_CN" : "获取备份文件失败。",
            "en" : "Failed to obtain backup file."
            },
        0x176: {
            "zh_CN" : "解锁管理员账户成功。", 
            "en" : "Admin account unlocked successfully."
            },
        0x177: {
            "zh_CN" : "参数错误，用户名未输入",
            "en" : "Incorrect parameters. User name cannot be empty. "
            },
        0x178: {
            "zh_CN" : "用户名不存在。",
            "en" : "User name does not exist."
            },
        0x179: {
            "zh_CN" : "解锁管理员账户失败",
            "en" : "Failed to unlock admin account."
            },
        0x17a: {
            "zh_CN" : "请输入新密码：",
            "en" : "Enter a new password:"
            },
        0x17b: {
            "zh_CN" : "密码强度弱，10-32位字符，数字、字母、大小写、特殊字符各一",
            "en" : "Weak password. A strong password must be 10-32 digits in length and include each of the following: numbers, uppercase letters, lowercase letters, and special characters."
            },
        0x17c: {
            "zh_CN" : "请再次输入密码：",
            "en" : "Re-enter password:"
            },
        0x17d: {
            "zh_CN" : "两次密码输入不同。请重新输入。",
            "en" : "You entered a different password. Please check and re-enter."
            },
        0x17e: {
            "zh_CN" : "密码重置成功",
            "en" : "Password reset successfully."
            },
        0x180: {
            "zh_CN" : "参数错误。用户名或密码未输入。",
            "en" : "Incorrect parameters. User name and password cannot be empty."
            },
        0x181: {
            "zh_CN" : "用户名不存在",
            "en" : "User name does not exist."
            },
        0x182: {
            "zh_CN" : "密码重置失败。", 
            "en" : "Failed to reset password."
            },
        0x183: {
            "zh_CN" : "欢迎使用天空卫士管理控制台",
            "en" : "Welcome to Skyguard management console"
            },
        0x184: {
            "zh_CN" : "请确认是否保存变更? Y/N(No):",
            "en" : "Are you sure you want to save the change? Y/N(No):"
            },
        0x185: {
            "zh_CN" : "输入错误",
            "en" : "Incorrect input"
            },
        0x186: {
            "zh_CN" : "请配置ITM服务器",
            "en" : "ITM server configuration"
            },
        0x187: {
            "zh_CN" : "请确认是否变更ITM服务器配置？Y/N(No):",
            "en" : "Are you sure you want to save the ITM server settings? Y/N (No):"
            },
        0x188: {
            "zh_CN" : "密码不能为空，请重新输入",
            "en" : "Password cannot be empty, please re-enter password"
            },
        0x189: {
            "zh_CN" : "服务端口(%d):",
            "en" : "Service port(%d):"
            },
        0x18a: {
            "zh_CN" : "用户名(%s):",
            "en" : "User name(%s):"
            },
        0x18b: {
            "zh_CN" : "ITM服务器配置",
            "en" : "ITM server settings"
            },
        0x18c: {
            "zh_CN" : "请确认是否需要兼容3.3版本的设备？Y/N(No)",
            "en" : "please confirm whether the device compatible with version 3.3.Y/N(NO):"
            }
    }  

