import datetime as dt


def set_datetime_double_xaxis(ax, times, hour_fontsize=10, date_fontsize=12, 
                         hour_interval: int|None=None, rotation=0, date_format="%m-%d"):
    """
    设置双行时间轴：上行显示小时，下行显示日期（日期只在第一次出现时显示）
    
    参数:
        ax: matplotlib axes对象
        times: datetime对象列表
        hour_fontsize: 小时标签字体大小
        date_fontsize: 日期标签字体大小
        hour_interval: 小时标签间隔（默认每6小时）
        rotation: 标签旋转角度
    
    返回:
        ax: 主轴（用于绘图和显示日期）
        ax_hour: 小时次轴
    """
    if hour_interval is None:
        tmp_hour = times[0].hour
        for i in [2, 3, 5, 7]:
            if tmp_hour % i == 0:
                hour_interval = i
                break

    times_ticks = times[::hour_interval]
    times_labels = [_time.strftime("%H") for _time in times_ticks]   

    dates_ticks = []
    dates_labels = []
    for t in times:
        date_str = t.strftime(date_format)
        if date_str not in dates_labels:
            dates_labels.append(date_str)
            dates_ticks.append(t)  
            if t not in times_ticks:
                hour_str = t.strftime("%H")
                times_ticks.append(t)
                times_labels.append(hour_str)

                for x in [-1, 1]:
                    if (t + dt.timedelta(hours=x)) in times_ticks:
                        times_ticks.remove(t + dt.timedelta(hours=x))
                        times_labels.remove((t + dt.timedelta(hours=x)).strftime("%H"))

    ax.set_xticks(times_ticks)
    ax.set_xticklabels(times_labels, fontsize=hour_fontsize, rotation=rotation)
    # ax.tick_params(axis='x', which='major', length=0)  # 隐藏主轴刻度线  

    main_spine_pos = ax.spines['bottom'].get_position()
    gap = hour_fontsize * 1.5
        
    secax  = ax.secondary_xaxis('bottom')
    secax.spines['bottom'].set_position(('outward', gap))
    secax.set_xticks(dates_ticks)
    secax.set_xticklabels(dates_labels, fontsize=date_fontsize, rotation=rotation)
    secax.tick_params(axis='x', which='both', length=0)  # 隐藏刻度线  
    secax.spines['bottom'].set_visible(False)    