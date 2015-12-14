from matplotlib import animation
from matplotlib import pyplot as plt
from IPython.display import HTML
from tempfile import NamedTemporaryFile
import base64


def image_stack_to_movie(images, frames=None, vmin=None, vmax=None,
                         figsize=(6, 5), cmap='CMRmap', fps=10):

    if frames is None:
        frames = images.shape[0]

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    im = plt.imshow(images[1], vmin=vmin, vmax=vmax, cmap=cmap,
                    interpolation='none')
    fig.colorbar(im)
    for item in ([ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(14)
        item.set_fontweight('bold')

    def animate(i):
        im.set_array(images[i])
        ax.set_title('Frame {}'.format(i), fontsize=16, fontweight='bold')
        return im,

    anim = animation.FuncAnimation(fig, animate, frames=frames,
                                   interval=1, blit=True)
    plt.close(anim._fig)
    return HTML(anim_to_html(anim, fps))


def anim_to_html(anim, fps):
    VIDEO_TAG = """<video controls>
    <source src="data:video/x-m4v;base64,{0}" type="video/mp4">
    Your browser does not support the video tag.
    </video>"""

    if not hasattr(anim, '_encoded_video'):
        with NamedTemporaryFile(suffix='.mp4') as f:
            anim.save(f.name, fps=fps, extra_args=['-vcodec', 'libx264',
                                                   '-pix_fmt', 'yuv420p'])
            video = open(f.name, "rb").read()
        anim._encoded_video = base64.b64encode(video)
    return VIDEO_TAG.format(anim._encoded_video.decode("utf-8"))
