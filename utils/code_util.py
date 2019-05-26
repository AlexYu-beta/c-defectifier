import re
def parse_header_body(code):
    """
    parse c header description and program body
    :param code:
    :return:
    """
    lines = code.split('\n')
    pattern_1 = re.compile('#include *<(.*)>|#include *"(.*)"|#include*<(.*)>|#include*"(.*)"')
    pattern_2 = re.compile('#define .*')
    pattern_3 = re.compile('\r|\n|\n\r|\r\n')
    lines = list(filter(lambda line: pattern_3.match(line.strip()) is None, lines))
    body = list(filter(lambda line: pattern_1.match(line.strip()) is None, lines))
    headers = list(filter(lambda line: pattern_1.match(line) is not None, lines))
    body_without_sharp_define = [line if pattern_2.match(line.strip()) is None else '' for line in body]
    sharp_define_in_body = [line for line in body if pattern_2.match(line.strip()) is not None]
    sharp_defines = len(sharp_define_in_body)
    headers = headers + sharp_define_in_body
    if len(headers) == 0:
        return "", code, 0
    return "\n".join(headers), "\n".join(body_without_sharp_define), sharp_defines


def construct_program(headers, body):
    """
    construct c source code from c header description and program body
    :param headers:
    :param body:
    :return:
    """
    # impl
    return headers + "\n" + body


if __name__ == '__main__':
    code_f = r'''#include <stdio.h>
char flag = 'N';
static int test = 20;
#define TR 1
int func (int a)
{
    if (a % 2 == 0)
        return a;
    else
        return a * 2;    
}

int main (int argc, char *argv[])
{
    int i,n,temp;
    int sum=0;
    scanf("%d\n", &n);
    for(i=0;i<n;i++)
    {
        scanf("%d", &temp);
        sum+=temp;
    }
    if(sum>10 && sum<20 && sum<30)
    {
        sum-=10;
    }
    if(func(sum)>test)
    {
        if(sum>30 && sum<40)
        {
            sum-=10;
        }
    }
    printf("%d\n",sum);
}'''
    code_db = r'''#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>



int main() {
    int n,m;
    scanf("%d %d",&n,&m);
    int i,j,k;
	char a[n][m];
    for(i=0;i<n;i++){
            scanf("%s",&a[i]);
    }
    i=0;j=0;
    int o=0,p=0,c=0,t=0,mt=m*n;
    int b[(m < n ? n : m)+1];
    for(i=2;i<(m < n ? n : m)+1;i++){
    	if(b[i]!=1){
    		b[i]=0;
    		j=2;
    		while(i*j<(m < n ? n : m)+1){
    			b[i*j]=1;
    			j++;
    		}
    	}
    }
    i=0; j=0;
    for(k=2;k<=(m < n ? n : m)/2+1;k++){
        t=0; 
        if(b[k]==0){
        for(i=0;i<n;i=i+k){
            for(j=0;j<m;j=j+k){
                c=0;
               for(o=0;o<k;o++){
                    for(p=0;p<k;p++){
                        if(i+o<n && j+p<m){
                            if(a[i+o][j+p]=='1'){
                                c++;    
                            }
                        }    
                    }
                    if((c*2>k*k && t+k*k-c>=mt) || (c*2<=k*k && t+c>=mt))
                    	break;
                }
                if(2*c>k*k)
                    t+=(k*k-c);
                else
                    t+=c;
                if(t>=mt)
					break;    
            }
        }
        if(mt>t){
            mt=t;
        }
    }
    }
    printf("%d\n",mt);
    return 0;
}'''
    headers, body = parse_header_body(code_f)
    print(headers)
