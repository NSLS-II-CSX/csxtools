from IPython.display import display, Javascript


def notebook_to_gist():
    js = """

function callback(out){
    console.log(out);
    window.open(out.content.text,'_blank');
}

var nb = IPython.notebook;
var kernel = IPython.notebook.kernel;
kernel.execute('import subprocess, os')

var command = "print("
command += "subprocess.run(['gist',";
command += "'" + nb.base_url + nb.notebook_path + "'.replace('/user','/home')]";
command += ", env=dict(os.environ, http_proxy='http://proxy:8888')";
command += ", stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip()";
command += ".replace('gist.github.com','nbviewer.jupyter.org/gist')"
command += ")";
console.log(command);
kernel.execute(command, {iopub: {output: callback}});"""

    return display(Javascript(js))
