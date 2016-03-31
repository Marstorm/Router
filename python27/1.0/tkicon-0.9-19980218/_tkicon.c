/*
 * tkIcon
 * $Id$
 *
 * change window icon on the fly
 *
 * history:
 * 98-02-03 fl  created
 * 98-02-16 fl  handle arbitrary RGBA images
 *
 * Copyright (c) 1998 Secret Labs AB.
 *
 * info@pythonware.com
 * http://www.pythonware.com
 *
 * --------------------------------------------------------------------
 * SOFTWARE LICENSE
 * --------------------------------------------------------------------
 *
 * This module is copyright (c) 1998 by Secret Labs AB
 *
 * By obtaining, using, and/or copying this software and/or its
 * associated documentation, you agree that you have read, understood,
 * and will comply with the following terms and conditions:
 * 
 * Permission to use, copy, modify, and distribute this software and its
 * associated documentation for any purpose and without fee is hereby
 * granted, provided that the above copyright notice appears in all
 * copies, and that both that copyright notice and this permission notice
 * appear in supporting documentation, and that the name of Secret Labs
 * AB is not used in advertising or publicity pertaining to distribution
 * of the software without specific, written prior permission.
 * 
 * SECRET LABS AB DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
 * INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN
 * NO EVENT SHALL SECRET LABS AB BE LIABLE FOR ANY SPECIAL, INDIRECT OR
 * CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
 * USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 * OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 *
 * --------------------------------------------------------------------
 */

#include "Python.h"

#define WIN32_LEAN_AND_MEAN
#include "windows.h"

/* ------------------------------------------------------------------- */
/* icon instance */

typedef struct {
    PyObject_HEAD
    HICON icon;
} IconObject;

staticforward PyTypeObject Icon_Type;

#if 0
void windows_error(char *msg)
{
    LPVOID lpMsgBuf;
    fprintf(stderr, "Windows Error: %s\n", msg);
    fprintf(stderr, "  GetLastError() => %d\n", GetLastError());
    FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER |
		  FORMAT_MESSAGE_FROM_SYSTEM,
		  NULL,
		  GetLastError(),
		  MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		  (LPTSTR) &lpMsgBuf,
		  0,
		  NULL 
                  );
    fprintf(stderr, "  FormatMessage() => %s\n", (char*) lpMsgBuf);
    LocalFree(lpMsgBuf);
}
#endif

/* ------------------------------------------------------------------- */
/* icon factory. */

static PyObject*
_icon_new(PyObject* self, PyObject* args)
{
    IconObject* p;
    HDC hdc;
    HBITMAP hbitmap;
    HBITMAP hmask;
    ICONINFO icon;
    BITMAPINFO info;
  
    int xsize, ysize;
    char *bitmap, *mask;
    int bitmapsize, masksize;
    if (!PyArg_ParseTuple(args, "(ii)s#s#", &xsize, &ysize,
                          &bitmap, &bitmapsize,
                          &mask, &masksize))
 	return NULL;

    /* FIXME: should check bitmapsize and masksize */

    /* allocate the instance */
    p = PyObject_NEW(IconObject, &Icon_Type);
    if (!p)
        return NULL; /* NEW raised an MemoryError */

    /* create bitmap (background must be 0!) */
    hdc = GetDC(NULL);

    memset(&info, 0, sizeof(info));
    info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    info.bmiHeader.biWidth = xsize;
    info.bmiHeader.biHeight = ysize;
    info.bmiHeader.biPlanes = 1;
    info.bmiHeader.biBitCount = 32; /* BGRX */
    info.bmiHeader.biCompression = BI_RGB;

    hbitmap = CreateCompatibleBitmap(hdc, xsize, ysize);
    SetDIBits(hdc, hbitmap, 0, ysize, bitmap, &info, DIB_RGB_COLORS);

    /* create foreground mask */
    hmask = CreateBitmap(xsize, ysize, 1, 1, mask);

    /* create icon from mask and (xor'ed) foreground bitmap */
    icon.fIcon = 1;
    icon.hbmMask  = hmask;
    icon.hbmColor = hbitmap;

    p->icon = CreateIconIndirect(&icon);

    DeleteObject(hmask);
    DeleteObject(hbitmap);

    ReleaseDC(NULL, hdc);

    return (PyObject*) p;
}

static void
_icon_dealloc(IconObject* self)
{
    DestroyIcon(self->icon);
    PyMem_DEL(self);
}

/* ------------------------------------------------------------------- */
/* attach icon to window */

static PyObject*
_icon_attach(IconObject* self, PyObject* args)
{
    HWND hwnd;

    long wnd_;
    if (!PyArg_ParseTuple(args, "l", &wnd_))
	return NULL;

    hwnd = (HWND) wnd_;

    while (GetParent(hwnd))
        hwnd = GetParent(hwnd);

    SendMessage(hwnd, WM_SETICON, ICON_BIG,   (LPARAM) self->icon);
    SendMessage(hwnd, WM_SETICON, ICON_SMALL, (LPARAM) self->icon);

    Py_INCREF(Py_None);
    return Py_None;
}

/* ------------------------------------------------------------------- */
/* type method table */

static struct PyMethodDef _icon_methods[] = {
    {"attach", (PyCFunction)_icon_attach, 1},
    {NULL, NULL}
};

/* ------------------------------------------------------------------- */
/* handle type attribute requests */

static PyObject*  
_icon_getattr(IconObject* self, char* name)
{
    PyObject* res;

    /* methods are looked up in the method table */
    res = Py_FindMethod(_icon_methods, (PyObject*) self, name);
    if (res)
	return res;

    PyErr_SetString(PyExc_AttributeError, name);
    return NULL;
}

/* ------------------------------------------------------------------- */
/* type descriptor */

statichere PyTypeObject Icon_Type = {
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size*/
    "TopazIcon"	,  		/*tp_name*/
    sizeof(IconObject),   	/*tp_size*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)_icon_dealloc,	/*tp_dealloc*/
    0,				/*tp_print*/
    (getattrfunc)_icon_getattr,	/*tp_getattr*/
    0,				/*tp_setattr*/
    0,				/*tp_compare*/
    0,				/*tp_repr*/
    0,                          /*tp_as_number */
    0,                          /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0                           /*tp_hash*/
};

/* -------------------------------------------------------------------- */
/* module interface */

static PyMethodDef _functions[] = {
    {"new", _icon_new, 1},
    {NULL, NULL}
};

void
#ifdef WIN32
__declspec(dllexport)
#endif
init_tkicon()
{
    /* patch the type descriptor. */
    Icon_Type.ob_type = &PyType_Type;

    /* register the module and its functions */
    Py_InitModule("_tkicon", _functions);
}
