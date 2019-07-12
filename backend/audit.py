
class AuditLogHandler:
    def __init__(self, log_file):
        self.log_file_obj = self._get_file(log_file)

    def _get_file(self, log_file):
        return open(log_file)

    def parse(self):
        cmd_list = []
        cmd_str = ''
        catch_write5_flag = False  # 处理tab补全
        for l in self.log_file_obj:
            # print(len(l.split()), l.split())
            line = l.split()
            try:
                pid, time_clock, io_call, char = line[0:4]
                print(pid, time_clock, io_call, char)
                if io_call.startswith('read(4'):
                    if char == '"\\10",':  # backspace
                        char = '[1<-del]'

                    # vim环境下,
                    if char == '"\\33OA",':
                        # char = '[up 1]'
                        char = '[↑]'
                    if char == '"\\33OB",':
                        # char = '[down 1]'
                        char = '[↓]'
                    if char == '"\\33OD",':
                        # char = '[1<-]'
                        char = '[←]'
                    if char == '"\\33OC",':
                        # char = '[->1]'
                        char = '[→]'

                    if char == '"\\33[2;2R",':  # 进入vim
                        continue
                    if char == '"\\33[>0;136;0c",':  # \33 Esc
                        char = '[---enter vim---]'
                    if char == '"\\33",':
                        char = '[Esc]'

                    # 命令行下,
                    if char == '"\\33[D",':
                        # char = '[1<-]'
                        char = '[←]'
                    if char == '"\\33[C",':
                        # char = '[->1]'
                        char = '[→]'
                    if char == '"\\33[A",':
                        # char = '[up 1]'
                        char = '[↑]'
                    if char == '"\\33[B",':
                        # char = '[down 1]'
                        char = '[↓]'

                    cmd_str += char.strip('"",')

                    if char == '"\\t",':  # tab补全
                        catch_write5_flag = True
                        continue
                    if char == '"\\r",':  # Enter键
                        cmd_list.append([time_clock, cmd_str])
                        cmd_str = ''  # 重置
                    if char == '"':  # 空格
                        cmd_str += ' '

                if catch_write5_flag:
                    if io_call.startswith('write(5'):
                        if char == '"\\7"':
                            pass
                        else:
                            cmd_str += char.strip('"",')  # "nfig ",
                            catch_write5_flag = False

            except Exception as e:
                print(e)

        print(cmd_list)
        return cmd_list


if __name__ == '__main__':
    parser = AuditLogHandler('/home/yangxl/ssh.log')
    parser.parse()